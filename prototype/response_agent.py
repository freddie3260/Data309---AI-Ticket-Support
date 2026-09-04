import requests

def generate_response(
        ticket,
        category,
        sentiment,
        escalation):

    prompt = f"""
    You are an experienced customer support specialist.

    Customer Ticket:
    {ticket}

    Ticket Category:
    {category}

    Customer Sentiment:
    {sentiment}

    Escalation Required:
    {escalation}

    Response Requirements:

    1. Acknowledge the customer's issue.
    2. Show empathy if sentiment is NEGATIVE.
    3. Provide category-specific guidance.
    4. Explain the next steps.
    5. Keep the response professional.
    6. Limit the response to 150 words.

    Category Guidance:

    Technical Issue:
    Provide troubleshooting guidance and explain expected next steps.

    Billing and Payment:
    Explain payment verification and billing review procedures.

    Return and Exchange:
    Explain return and exchange procedures.

    Account:
    Provide account recovery, verification, password reset,
    or account access guidance.

    Sales and Pre-sales:
    Provide product information and purchasing advice.

    IT and Technical Support:
    Provide technical support guidance and troubleshooting advice.

    General:
    Provide general customer service assistance.

    Generate a professional customer support response.
    """

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi4-mini",   # Change if you're using another model
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        data = response.json()

        # Debug information
        #print("\nReturned JSON:")
        #print(data)

        if "response" in data:
            return data["response"]

        if "error" in data:
            return f"Ollama Error: {data['error']}"

        return "Unexpected Ollama response format."

    except Exception as e:
        return f"Connection Error: {str(e)}"


def main():
    # # Testing
    from classifier_agent import generate_category
    from sentiment_agent import generate_sentiment
    from escalation_agent import check_escalation

    ticket = """
    I cannot log into my account and I am very frustrated.
    """

    # AI agent for check ticket type
    category = generate_category(ticket)     # Classification
    sentiment_result = generate_sentiment(ticket)   # Sentiment

    ticket_category = category["labels"][0]
    sentiment_label = sentiment_result[0]["label"]

    # Check escalation is needed or not
    escalation = check_escalation(ticket, ticket_category, sentiment_label)

    # show ticket type and escalation state
    # print(ticket_category)
    # print(sentiment_label)
    # print(escalation)

    # Response Generator (Ollama)
    response_text = generate_response(
        ticket,
        ticket_category,
        sentiment_label,
        escalation
    )

    print(response_text)

    # Old code
    # ticket = """
    #  I cannot log into my account and I am very frustrated.
    #  """

    # labels = [
    #     "Technical Issue",
    #     "Billing and Payment",
    #     "Return and Exchange",
    #     "Account",
    #     "Sales and Pre-sales",
    #     "IT and Technical Support",
    #     "General"
    # ]

    # # Classification
    # from transformers import pipeline
    # classifier = pipeline(
    #     "zero-shot-classification",
    #     model="facebook/bart-large-mnli"
    # )

    # sentiment_model = pipeline(
    #     "sentiment-analysis"
    # )

    # classification = classifier(
    #     ticket,
    #     candidate_labels=labels
    # )

    # category = classification["labels"][0]

    # # Sentiment
    # sentiment_result = sentiment_model(
    #     ticket
    # )

    # sentiment_label = sentiment_result[0]["label"]

    # # Escalation
    # if sentiment_label == "NEGATIVE":
    #     escalation = "YES"
    # else:
    #     escalation = "NO"

    # # Response Generator (Ollama)
    # response_text = generate_response(
    #     ticket,
    #     category,
    #     sentiment_label,
    #     escalation
    # )

    # print(response_text)

if __name__ == "__main__":
    main()