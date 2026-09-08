from classifier_agent import billing_payment_check

ESCALATION_CHECK = 0
NEGATIVE_SENTIMENT = 0
def check_escalation(body, category, sentiment, status):
    global ESCALATION_CHECK
    global NEGATIVE_SENTIMENT
    ans = False

    # All escalation step
    if escalation_solve(status) == False:
        return "NO", ESCALATION_CHECK
    
    if ESCALATION_CHECK != 1 and escalation_sentiment(sentiment) == False: # Sentiment check (don't check for the first time)
        if NEGATIVE_SENTIMENT >= 2: # if the sentiment is negative two time or more then escalate
            ans = True
        else:
            NEGATIVE_SENTIMENT += 1
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


def escalation_solve(status):
    """
    check ticket status
    """
    if status == "Solved":
        return False # if ticket solve then don't escalate
    return True

def reset_escalation():
    global ESCALATION_CHECK
    global NEGATIVE_SENTIMENT

    ESCALATION_CHECK = 0
    NEGATIVE_SENTIMENT = 0



def main():
    # Test & Not agent irrelevant
    print(
        escalation_sentiment("NEGATIVE")
    )

if __name__ == "__main__":
    main()