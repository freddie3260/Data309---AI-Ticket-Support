import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_classifier():
    """Load Model"""
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )


def generate_category(ticket):
    """
    generate category base on the ticket type
    """
    classifier = load_classifier()
    labels = [
        "Technical Issue",
        "Billing and Payment",
        "Return and Exchange",
        "Account",
        "Sales and Pre-sales", 
        "IT and Technical Support", 
        "General",
        "Shipping and Delivery"
    ]

    # Generate category base on ticket info
    result = classifier(
        ticket,
        candidate_labels = labels
    )

    return result


def main():
    # Test case
    ticket = """
    I cannot log into my account and I am very frustrated.
    """

    test = generate_category(ticket)

    print("Predicted Category:")
    print(test["labels"][0])

    print("Confidence:")
    print(test["scores"][0])

if __name__ == "__main__":
    main()