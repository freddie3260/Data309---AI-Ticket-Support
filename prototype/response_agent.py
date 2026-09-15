import requests

def generate_response(
    ticket,
    category,
    sentiment,
    escalation,
    status):

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
        #when ticket solved
    if status == "Solved":
        prompt = f"""
            You are a professional customer support specialist.

            The customer's issue has been successfully resolved.

            Customer Ticket:
            {ticket}

            Ticket Category:
            {category}

            Customer Sentiment:
            {sentiment}

            Your task is to write a final response confirming that
            the customer's issue has been resolved.

            Response Requirements:

            1. Acknowledge the customer's original issue.
            2. Clearly confirm that the issue has been resolved.
            3. Briefly explain the resolution if the information is available.
            4. Be polite, professional, and reassuring.
            5. If the customer was frustrated or negative, show empathy.
            6. Thank the customer for their patience.
            7. Tell the customer to contact support again if the issue returns.
            8. Do not invent actions or information that are not provided.
            9. Do not mention AI, language models, prompts, or internal processes.
            10. Keep the response under 100 words.

            Generate the final customer support response.
            """

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi4-mini",   #change if we want another model
                "prompt": prompt,
                "stream": False
                },
            timeout=120
            )
        response.raise_for_status()

        data = response.json()

        

        if "response" in data:
            return True, data["response"]

        if "error" in data:
            return False, f"Ollama Error: {data['error']}"

        return False, "Unexpected Ollama response format."

    except requests.exceptions.ConnectionError:
        return False, (
            "Could not connect to Ollama. Make sure it's running "
            "('ollama serve') and that 'phi4-mini' has been pulled "
            "('ollama pull phi4-mini')."
        )
    except requests.exceptions.Timeout:
        return False, "Ollama took too long to respond (timed out after 120s)."
    except Exception as e:
        return False, f"Unexpected error while generating a response: {str(e)}"


def main():
    
    from classifier_agent import generate_category
    from sentiment_agent import generate_sentiment
    from escalation_agent import check_escalation

    ticket = """
    I cannot log into my account and I am very frustrated.
    """

    #check ticket type
    category = generate_category(ticket)     
    sentiment_result = generate_sentiment(ticket)   

    ticket_category = category["labels"][0]
    sentiment_label = sentiment_result[0]["label"]

    #check escalation
    escalation = check_escalation(ticket, ticket_category, sentiment_label)

    

    #response
    response_text = generate_response(
        ticket,
        ticket_category,
        sentiment_label,
        escalation
    )

    print(response_text)

    

if __name__ == "__main__":
    main()