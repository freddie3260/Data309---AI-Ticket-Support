from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

ticket = """
I cannot log into my account and I am very frustrated.
"""

labels = [
     "Technical Issue",
    "Billing and Payment",
    "Return and Exchange",
    "Account",
    "Sales and Pre-sales", "IT and Technical Support", "General"
]

result = classifier(
    ticket,
    candidate_labels=labels
)

print("Predicted Category:")
print(result["labels"][0])

print("Confidence:")
print(result["scores"][0])