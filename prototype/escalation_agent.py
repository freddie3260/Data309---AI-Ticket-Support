from classifier_agent import billing_payment_check

ESCALATION_CHECK = 1

def check_escalation(body, category, sentiment):
    global ESCALATION_CHECK
    ans = False

    # All escalation step
    if escalation_sentiment(sentiment) == False: # Sentiment check
        ans = True
    if category in ["Billing and Payment"]: # Special step needed for billing and payment category
        category = billing_payment_check(body)

    if category in ["Sales and Pre-sales", "Payment"]: # if in this category than we issue ticket to human
        ans = True
    # elif category in ["Technical Issue", "Return and Exchange", "Account", "Billing", "IT and Technical Support", "General", "Shipping and Delivery"]: # to AI
        
    # if user ask 3 times or escalation is needed then escalate
    if ESCALATION_CHECK >= 3 or ans:
        return "YES", ESCALATION_CHECK

    ESCALATION_CHECK += 1

    return "NO", ESCALATION_CHECK

    


def escalation_sentiment(sentiment):
    """
    check ticket need to be escalate or not
    """
    # if sentiment are negative then escalate
    if sentiment == "NEGATIVE":
        return True
    else:
        return False


def main():
    # Test & Not agent irrelevant
    print(
        escalation_sentiment("NEGATIVE")
    )

if __name__ == "__main__":
    main()