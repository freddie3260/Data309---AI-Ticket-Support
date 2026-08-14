import streamlit as st

from transformers import pipeline

from response_agent import generate_response

# ------------------------------------
# Load models (once)
# ------------------------------------

@st.cache_resource
def load_models():

    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

    sentiment = pipeline(
        "sentiment-analysis"
    )

    return classifier, sentiment


classifier, sentiment_model = load_models()


# ------------------------------------
# Page Title
# ------------------------------------

st.title(
    "📨 Automated Customer Support Ticket System"
)

st.write(
    "Enter a customer ticket and analyse it."
)

# ------------------------------------
# Ticket Input
# ------------------------------------

ticket = st.text_area(
    "Customer Ticket",
    height=200
)

# ------------------------------------
# Analyse Button
# ------------------------------------

if st.button("Analyse Ticket"):

    labels = [
        "Technical Issue",
        "Billing and Payment",
        "Return and Exchange",
        "Account",
        "Sales and Pre-sales",
        "IT and Technical Support",
        "General"
    ]

    # Classification
    classification = classifier(
        ticket,
        candidate_labels=labels
    )

    category = classification["labels"][0]

    # Sentiment
    sentiment_result = sentiment_model(
        ticket
    )

    sentiment_label = sentiment_result[0]["label"]

    # Escalation
    if sentiment_label == "NEGATIVE":
        escalation = "YES"
    else:
        escalation = "NO"

    # Response Generator (Ollama)
    response_text = generate_response(
        ticket,
        category,
        sentiment_label,
        escalation
    )

    # Display Results

    st.subheader("Category")
    st.success(category)

    st.subheader("Sentiment")
    st.info(sentiment_label)

    st.subheader("Escalation Required")
    st.warning(escalation)

    st.subheader("Generated Response")
    st.write(response_text)

    st.metric("Category", category)

    st.metric("Sentiment", sentiment_label)

    st.progress(
    classification["scores"][0]
)