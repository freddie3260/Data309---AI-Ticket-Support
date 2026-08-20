def check_escalation(sentiment):
    """
    check ticket need to be escalate or not
    """
    # if sentiment are negative then escalate
    if sentiment == "NEGATIVE":
        return "YES"
    else:
        return "NO"


def main():
    # Test & Not agent irrelevant
    print(
        check_escalation("NEGATIVE")
    )

if __name__ == "__main__":
    main()