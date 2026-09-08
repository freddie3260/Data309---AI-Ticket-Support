import streamlit as st

from response_agent import generate_response
from classifier_agent import generate_category, check_status
from sentiment_agent import generate_sentiment
from escalation_agent import check_escalation, reset_escalation

# save ticket info
if "tickets" not in st.session_state:
    st.session_state.tickets = None

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
    # if the ticket status is solved or not
    ticket_status = check_status(ticket)["labels"][0]

    # AI agent for check ticket type
    category = generate_category(ticket)     # Classification
    sentiment = generate_sentiment(ticket)   # Sentiment
        
    ticket_type = category["labels"][0]
    category_score = category["scores"][0]
    sentiment_type = sentiment[0]["label"]


    escalation, esc_num = check_escalation(ticket, 
                                        ticket_type, 
                                        sentiment_type, 
                                        ticket_status) # Escalation

    # Response Generator (Ollama)
    response_text = generate_response(
            ticket,
            ticket_type,
            sentiment_type,
            escalation,
            ticket_status
        )
    # Save ticket information
    if st.session_state.tickets == None:
        st.session_state.tickets = {
            "ticket": ticket,
            "category": ticket_type,
            "category_score": category_score,
            "sentiment": sentiment_type,
            "escalation": escalation,
            "escalation_count": esc_num,
            "status": ticket_status,
            "response": response_text
        }
    else:
        st.session_state.tickets.update({
            "category": ticket_type,
            "sentiment": sentiment_type,
            "escalation": escalation,
            "escalation_count": esc_num,
            "status": ticket_status,
            "response": response_text
        })

    # Display Results
    st.subheader("Category")
    st.success(ticket_type) # Category
    st.progress(category_score) # Confidence Score for Category

    st.subheader("Sentiment")
    st.info(sentiment_type) # Sentiment

    st.subheader("Escalation Required")
    st.warning(escalation) # Escalation

    st.subheader("Generated Response")
    st.write(response_text) # AI Response

    st.subheader("esc_check")
    st.write(esc_num)

    st.subheader("ticket_status")
    st.write(ticket_status)



# ------------------------------------
# New Analyse Button
# ------------------------------------

if st.button("New Ticket"):
    st.session_state.tickets = None
    reset_escalation()
    st.rerun()


def main():
    ticket = """
    I cannot log into my account and I am very frustrated.
    """
    category = generate_category(ticket)     # Classification
    sentiment = generate_sentiment(ticket)   # Sentiment

    ticket_type = category["labels"][0]
    category_score = category["scores"][0]
    sentiment_type = sentiment[0]["label"]

    escalation, num = check_escalation(ticket, ticket_type, sentiment_type) # Escalation

    # Response Generator (Ollama)
    response_text = generate_response(
        ticket,
        ticket_type,
        sentiment_type,
        escalation
    )

    # print(response_text)
    # print(num)

RUN_TEST = False
if __name__ == "__main__":
    if RUN_TEST:
        main()

