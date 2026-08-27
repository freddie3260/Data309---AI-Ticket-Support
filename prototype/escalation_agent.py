from classifier_agent import billing_payment_check


def check_escalation(body, category, sentiment):
    ans = []

    # All escalation step
    ans.append(escalation_sentiment(sentiment)) # Sentiment check
    if category in ["Billing and Payment"]: # Special step needed for billing and payment category
        category = billing_payment_check(body)

    if category in ["Sales and Pre-sales", "Payment"]: # if in this category than we issue ticket to human
        ans.append(True)
    elif category in ["Technical Issue", "Return and Exchange", "Account", "Billing", "IT and Technical Support", "General", "Shipping and Delivery"]: # to AI
        ans.append(False)
        
    

    # if all step is good than return YES
    if all(ans):
        return "YES" # don't escalate
    else:
        return "NO" # escalate




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
        check_escalation("NEGATIVE")
    )

if __name__ == "__main__":
    main()