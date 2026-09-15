from pathlib import Path

import pandas as pd
import streamlit as st

from response_agent import generate_response
from classifier_agent import generate_category, check_status
from sentiment_agent import generate_sentiment
from escalation_agent import check_escalation, reset_escalation

#page config

st.set_page_config(
    page_title="Automated Customer Support Ticket System",
    page_icon="📨",
    layout="wide",
)


APP_DIR = Path(__file__).resolve().parent
SAMPLE_TICKETS_PATH = APP_DIR.parent / "Data Cleaning" / "tickets_clean_400_1.xlsx"


@st.cache_data
def load_sample_tickets():
    """Load the labelled 400-ticket sample, if it's present."""
    if not SAMPLE_TICKETS_PATH.exists():
        return None
    try:
        return pd.read_excel(SAMPLE_TICKETS_PATH)
    except Exception:
        return None
    
#session state setup


if "tickets" not in st.session_state:
    st.session_state.tickets = None


if st.session_state.get("_clear_ticket_form", False):
    st.session_state.ticket_input = ""
    st.session_state.account_input = ""
    st.session_state._clear_ticket_form = False


#Title

st.title("📨 Automated Customer Support Ticket System")

#new ticket

if st.button("New Ticket"):
    st.session_state.tickets = None
    reset_escalation()
    st.session_state._clear_ticket_form = True
    st.rerun()

st.write("Enter a customer ticket and analyse it.")

#ticket loader


sample_df = load_sample_tickets()

if sample_df is not None and "body" in sample_df.columns:
    with st.expander("Load a sample ticket (optional)"):
        sample_options = list(sample_df.index)
        selected_idx = st.selectbox(
            "Choose a sample ticket",
            options=sample_options,
            format_func=lambda i: (str(sample_df.loc[i, "body"])[:80] + "…"),
        )
        if st.button("Load into form below"):
            st.session_state.ticket_input = str(sample_df.loc[selected_idx, "body"])
            st.session_state.account_input = ""
            st.rerun()


#Ticket input


with st.form("ticket_form"):
    account_number = st.text_input(
        "Customer Account Number (optional)",
        key="account_input",
        help=(
            "Kept separate from the ticket text on purpose — mixing account "
            "numbers or other identifiers into the ticket body has been "
            "shown to confuse the category classifier."
        ),
    )
    ticket = st.text_area(
        "Customer Ticket",
        key="ticket_input",
        height=200,
    )
    submitted = st.form_submit_button("Analyse Ticket")


#analyse ticket


if submitted:
    if not ticket.strip():
        st.warning("Please enter a ticket before analysing.")
    else:
        with st.spinner("Classifying ticket…"):
            #solved or not
            ticket_status = check_status(ticket)["labels"][0]

            #ticket type
            category = generate_category(ticket)     
            sentiment = generate_sentiment(ticket)   

            ticket_type = category["labels"][0]
            category_score = category["scores"][0]
            sentiment_type = sentiment[0]["label"]

        with st.spinner("Checking escalation rules…"):
            escalation, esc_num = check_escalation(
                ticket,
                ticket_type,
                sentiment_type,
                ticket_status,
            )  
            #escalation

        with st.spinner("Drafting a response…"):
            #response 
            response_ok, response_text = generate_response(
                ticket,
                ticket_type,
                sentiment_type,
                escalation,
                ticket_status,
            )

        #save info
        st.session_state.tickets = {
            "ticket": ticket,
            "account_number": account_number,
            "category": ticket_type,
            "category_score": category_score,
            "sentiment": sentiment_type,
            "escalation": escalation,
            "escalation_count": esc_num,
            "status": ticket_status,
            "response": response_text,
            "response_ok": response_ok,
        }

        
        #display results
        

        result_col1, result_col2, result_col3 = st.columns(3)

        with result_col1:
            st.metric("Category", ticket_type, f"{category_score:.0%} confidence")

        with result_col2:
            st.metric("Sentiment", sentiment_type)

        with result_col3:
            st.metric("Ticket Status", ticket_status)

        if escalation == "YES":
            st.error("🚨 Escalation required — route this ticket to a human agent.")
        else:
            st.success("✅ No escalation needed right now.")

        with st.expander("Escalation summary (for human hand-off)"):
            st.write(f"**Category:** {ticket_type}")
            st.write(f"**Sentiment:** {sentiment_type}")
            st.write(f"**Ticket status:** {ticket_status}")
            st.write(f"**Times this ticket has been re-submitted:** {esc_num}")
            if account_number:
                st.write(f"**Customer account number:** {account_number}")
            st.write("**Original ticket text:**")
            st.write(ticket)

        st.subheader("Generated Response")
        if response_ok:
            st.write(response_text)
        else:
            st.error(response_text)


def main():
    ticket = """
    I cannot log into my account and I am very frustrated.
    """
    category = generate_category(ticket)     
    sentiment = generate_sentiment(ticket)   

    ticket_type = category["labels"][0]
    category_score = category["scores"][0]
    sentiment_type = sentiment[0]["label"]

    escalation, num = check_escalation(ticket, ticket_type, sentiment_type, "Not Solved")  

    #response generator
    response_ok, response_text = generate_response(
        ticket,
        ticket_type,
        sentiment_type,
        escalation,
        "Not Solved",
    )

    #print(response_text)
    #print(num)

RUN_TEST = False
if __name__ == "__main__":
    if RUN_TEST:
        main()
