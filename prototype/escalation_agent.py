import streamlit as st
from classifier_agent import billing_payment_check


def _init_escalation_state():
    """Make sure the escalation counters exist for this browser session."""
    if "escalation_check" not in st.session_state:
        st.session_state.escalation_check = 0
    if "negative_sentiment" not in st.session_state:
        st.session_state.negative_sentiment = 0


def check_escalation(body, category, sentiment, status):
    _init_escalation_state()
    ans = False

    # All escalation step
    if escalation_solve(status) == False:
        return "NO", st.session_state.escalation_check

    if st.session_state.escalation_check > 0:
        if escalation_sentiment(sentiment) == True:  # Sentiment check (don't check for the first time)
            if st.session_state.negative_sentiment >= 1:  # if the sentiment is negative two time or more then escalate
                ans = True
            else:
                st.session_state.negative_sentiment += 1

    if category in ["Billing and Payment"]:  # Special step needed for billing and payment category
        result = billing_payment_check(body)
        category = result["labels"][0]  # top predicted sub-label: "Billing" or "Payment"

    if category in ["Sales and Pre-sales", "Payment"]:  # if in this category than we issue ticket to human
        ans = True
    # elif category in ["Technical Issue", "Return and Exchange", "Account", "Billing", "IT and Technical Support", "General", "Shipping and Delivery"]: # to AI

    # if user ask 3 times or escalation is needed then escalate
    if st.session_state.escalation_check >= 3 or ans:
        return "YES", st.session_state.escalation_check

    st.session_state.escalation_check += 1

    return "NO", st.session_state.escalation_check


def escalation_sentiment(sentiment):
    """
    check ticket need to be escalate or not
    """
    # if sentiment are negative then escalate
    if sentiment == "NEGATIVE":
        return True
    else:
        return False


def escalation_solve(status):
    """
    check ticket status
    """
    if status == "Solved":
        return False  # if ticket solve then don't escalate
    return True


def reset_escalation():
    st.session_state.escalation_check = 0
    st.session_state.negative_sentiment = 0


def main():
    # Test & Not agent irrelevant
    print(
        escalation_sentiment("NEGATIVE")
    )

if __name__ == "__main__":
    main()
