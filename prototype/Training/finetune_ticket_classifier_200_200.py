# -*- coding: utf-8 -*-
"""
finetune_ticket_classifier_200_200.py
=====================================
Fine-tune facebook/bart-large-mnli on 200 tickets,
then evaluate on the held-out 200 tickets.

Input : prototype_results_1.xlsx  (columns: body, gold_category)
Output: ./ticket_classifier_bart_200/  (model + tokenizer + label map + predictions)

Usage:
    python finetune_ticket_classifier_200_200.py
"""

import os
import json
import random
from collections import Counter

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from datasets import Dataset, Features, Value, ClassLabel
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
)

# ============================================================
# 0. Configuration
# ============================================================
INPUT_FILE   = "prototype_results_1.xlsx"
SHEET_NAME   = "Sheet1"
MODEL_NAME   = "facebook/bart-large-mnli"
OUTPUT_DIR   = "ticket_classifier_bart_200"

TEXT_COL     = "body"
LABEL_COL    = "gold_category"

# ---- Data split sizes -------------------------------------
N_TEST       = 200     # exactly 200 held-out samples for final evaluation
VAL_FRACTION = 0.15    # 15% of the remaining 200 for validation
USE_VALIDATION = True  # set False to use all 200 for training (no early stopping)

# ---- Training hyperparameters -----------------------------
MAX_LEN       = 512
SEED          = 42
NUM_EPOCHS    = 5
BATCH_SIZE    = 8      # reduce to 4 if you hit OOM
LR            = 2e-5
WEIGHT_DECAY  = 0.01
WARMUP_RATIO  = 0.1
MAX_GRAD_NORM = 1.0
FP16          = torch.cuda.is_available()

# ---- Reproducibility --------------------------------------
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. Load data
# ============================================================
def load_data(path: str, sheet: str) -> pd.DataFrame:
    """Load Excel, keep only text + label, drop NaN / empty / duplicates."""
    df = pd.read_excel(path, sheet_name=sheet)

    missing = [c for c in [TEXT_COL, LABEL_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Found: {list(df.columns)}")

    df = df[[TEXT_COL, LABEL_COL]].dropna()
    df[TEXT_COL] = df[TEXT_COL].astype(str).str.strip()
    df[LABEL_COL] = df[LABEL_COL].astype(str).str.strip()

    df = df[df[TEXT_COL].str.len() > 0]
    before = len(df)
    df = df.drop_duplicates(subset=[TEXT_COL, LABEL_COL]).reset_index(drop=True)
    print(f"Loaded {before} rows, {len(df)} after dedup.")
    return df


# ============================================================
# 2. Label mapping
# ============================================================
def build_label_map(df: pd.DataFrame):
    """Sorted unique labels -> fixed label2id / id2label."""
    labels = sorted(df[LABEL_COL].unique().tolist())
    label2id = {label: i for i, label in enumerate(labels)}
    id2label = {i: label for label, i in label2id.items()}
    return label2id, id2label


# ============================================================
# 3. Fixed 200/200 split
# ============================================================
def split_200_200(df: pd.DataFrame, label2id: dict, id2label: dict):
    """
    Split data into:
      - test_df : exactly 200 rows (stratified, never used for training)
      - train_df: the remaining rows
      - val_df  : VAL_FRACTION of train_df (if USE_VALIDATION)
    """
    df = df.copy()
    df["label"] = df[LABEL_COL].map(label2id)

    if N_TEST >= len(df):
        raise ValueError(f"N_TEST={N_TEST} must be smaller than dataset size {len(df)}")

    # Stratified test split of exactly N_TEST rows
    train_pool_df, test_df = train_test_split(
        df,
        test_size=N_TEST,
        stratify=df["label"],
        random_state=SEED,
    )

    if USE_VALIDATION:
        train_df, val_df = train_test_split(
            train_pool_df,
            test_size=VAL_FRACTION,
            stratify=train_pool_df["label"],
            random_state=SEED,
        )
    else:
        train_df, val_df = train_pool_df, None

    print(f"\nSplit sizes -> Train: {len(train_df)}"
          f" | Val: {len(val_df) if val_df is not None else 0}"
          f" | Test: {len(test_df)}")

    features = Features({
        TEXT_COL: Value("string"),
        "label": ClassLabel(names=[id2label[i] for i in range(len(id2label))]),
    })

    # --- 關鍵修正：preserve_index=False ---
    train_ds = Dataset.from_pandas(
        train_df[[TEXT_COL, "label"]].reset_index(drop=True),
        features=features,
        preserve_index=False,
    )
    val_ds = (
        Dataset.from_pandas(
            val_df[[TEXT_COL, "label"]].reset_index(drop=True),
            features=features,
            preserve_index=False,
        )
        if val_df is not None else None
    )
    test_ds = Dataset.from_pandas(
        test_df[[TEXT_COL, "label"]].reset_index(drop=True),
        features=features,
        preserve_index=False,
    )

    return train_ds, val_ds, test_ds, test_df, train_df


# ============================================================
# 4. Tokenization
# ============================================================
def tokenize(train_ds, val_ds, test_ds, tokenizer):
    def _tok(examples):
        return tokenizer(
            examples[TEXT_COL],
            truncation=True,
            max_length=MAX_LEN,
        )

    train_ds = train_ds.map(_tok, batched=True)
    if val_ds is not None:
        val_ds = val_ds.map(_tok, batched=True)
    test_ds = test_ds.map(_tok, batched=True)
    return train_ds, val_ds, test_ds


# ============================================================
# 5. Class weights (handles imbalance)
# ============================================================
def compute_class_weights(labels_array, num_labels: int):
    """Inverse-frequency weights for CrossEntropyLoss."""
    labels_array = np.array(labels_array)
    counts = np.bincount(labels_array, minlength=num_labels)
    counts = np.where(counts == 0, 1, counts)
    weights = len(labels_array) / (num_labels * counts)
    print("\nTrain class counts :", counts.tolist())
    print("Train class weights:", np.round(weights, 3).tolist())
    return torch.tensor(weights, dtype=torch.float)


# ============================================================
# 6. Weighted Trainer
# ============================================================
class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            loss_fct = torch.nn.CrossEntropyLoss(
                weight=self.class_weights.to(logits.device)
            )
        else:
            loss_fct = torch.nn.CrossEntropyLoss()

        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))

        # 關鍵：只回傳 logits，不要回傳整個 outputs
        if return_outputs:
            return loss, {"logits": logits}
        return loss


# ============================================================
# 7. Metrics
# ============================================================
def compute_metrics(eval_pred):
    logits, labels = eval_pred

    if isinstance(logits, tuple):
        logits = logits[0]
    if hasattr(logits, "logits"):
        logits = logits.logits

    logits = np.array(logits)
    labels = np.array(labels).reshape(-1)

    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "macro_f1": f1_score(labels, preds, average="macro"),
        "weighted_f1": f1_score(labels, preds, average="weighted"),
    }

# ============================================================
# 8. Main
# ============================================================
def main():
    print("=" * 60)
    print("Loading data")
    print("=" * 60)
    df = load_data(INPUT_FILE, SHEET_NAME)

    print("\nFull category distribution:")
    print(df[LABEL_COL].value_counts())

    label2id, id2label = build_label_map(df)
    num_labels = len(label2id)
    print(f"\nNumber of labels: {num_labels}")
    print("Label map:", label2id)

    with open(os.path.join(OUTPUT_DIR, "label_map.json"), "w") as f:
        json.dump({"label2id": label2id, "id2label": id2label}, f, indent=2)

    # 200 / 200 split
    train_ds, val_ds, test_ds, test_df, train_df = split_200_200(df, label2id, id2label)

    print("\nTest set category distribution:")
    print(test_df[LABEL_COL].value_counts())

    # Tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds, val_ds, test_ds = tokenize(train_ds, val_ds, test_ds, tokenizer)

    # Model
    print("\nLoading model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )

    # Class weights from training labels only
    class_weights = compute_class_weights(train_ds["label"], num_labels)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # TrainingArguments
    use_val = val_ds is not None
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch" if use_val else "no",
        save_strategy="epoch" if use_val else "no",
        logging_strategy="steps",
        logging_steps=10,
        learning_rate=LR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        weight_decay=WEIGHT_DECAY,
        warmup_steps=WARMUP_RATIO,
        max_grad_norm=MAX_GRAD_NORM,
        load_best_model_at_end=use_val,
        metric_for_best_model="macro_f1" if use_val else None,
        greater_is_better=True,
        save_total_limit=2,
        fp16=FP16,
        report_to="none",
        seed=SEED,
    )

    callbacks = [EarlyStoppingCallback(early_stopping_patience=2)] if use_val else []

    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=callbacks,
    )

    # ---- Train -------------------------------------------------
    print("\n" + "=" * 60)
    print("Starting training on 200-sample train pool")
    print("=" * 60)
    trainer.train()

    if use_val:
        print("\n" + "=" * 60)
        print("Validation results")
        print("=" * 60)
        print(trainer.evaluate(val_ds))

    # ---- Final evaluation on the held-out 200 ------------------
    print("\n" + "=" * 60)
    print("FINAL evaluation on the held-out 200 test samples")
    print("=" * 60)
    test_metrics = trainer.evaluate(test_ds)
    print(test_metrics)

    # Detailed report
        # ---- 取得 test set 的預測結果 ----
    preds_output = trainer.predict(test_ds)

    # 拆解 predictions，取出乾淨的 logits
    logits = preds_output.predictions
    if isinstance(logits, tuple):
        logits = logits[0]
    if hasattr(logits, "logits"):
        logits = logits.logits
    logits = np.array(logits, dtype=np.float32)      # shape: (N, num_labels)

    y_true = np.array(preds_output.label_ids).reshape(-1)
    y_pred = np.argmax(logits, axis=-1)

    target_names = [id2label[i] for i in range(num_labels)]

    print("\nClassification report (test set, 200 samples):")
    print(classification_report(y_true, y_pred, target_names=target_names, digits=3))

    print("\nConfusion matrix (rows=true, cols=pred):")
    cm = confusion_matrix(y_true, y_pred)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print(cm_df)

    # Save artifacts
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # 用同一份 logits 計算信心分數
    probs = torch.softmax(torch.tensor(logits, dtype=torch.float32), dim=-1)
    confidences = probs.max(dim=-1).values.numpy()

    test_df = test_df.reset_index(drop=True)
    test_df["pred_label"] = [id2label[i] for i in y_pred]
    test_df["correct"] = (test_df["label"].values == y_pred)
    test_df["confidence"] = confidences
    test_df.to_excel(os.path.join(OUTPUT_DIR, "test_predictions.xlsx"), index=False)
    cm_df.to_csv(os.path.join(OUTPUT_DIR, "confusion_matrix.csv"))

    print(f"\nModel and reports saved to ./{OUTPUT_DIR}")


if __name__ == "__main__":
    main()