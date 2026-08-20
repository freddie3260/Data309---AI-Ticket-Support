import streamlit as st

from response_agent import generate_response
from classifier_agent import generate_category
from sentiment_agent import generate_sentiment
from escalation_agent import check_escalation

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

    # AI agent for check ticket type
    category = generate_category(ticket)     # Classification
    sentiment = generate_sentiment(ticket)   # Sentiment
    escalation = check_escalation(sentiment) # Escalation

    ticket_type = category["labels"][0]
    category_score = category["score"][0]
    sentiment_type = sentiment[0]["label"]

    # Response Generator (Ollama)
    response_text = generate_response(
        ticket,
        ticket_type,
        sentiment_type,
        escalation
    )

    # Display Results
    st.subheader("Category")
    st.success(ticket_type) # Category

    st.subheader("Sentiment")
    st.info(sentiment_type) # Sentiment

    st.subheader("Escalation Required")
    st.warning(escalation) # Escalation

    st.subheader("Generated Response")
    st.write(response_text) # AI Response

    st.metric("Category", ticket_type) 

    st.metric("Sentiment", sentiment_type)

    st.progress(category_score) # Confidence Score for Category