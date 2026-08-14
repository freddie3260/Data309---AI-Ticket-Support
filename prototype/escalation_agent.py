def check_escalation(sentiment):

    if sentiment == "NEGATIVE":
        return "ESCALATE"

    return "NORMAL"

print(
    check_escalation("NEGATIVE")
)