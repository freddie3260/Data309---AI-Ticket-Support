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