import pandas as pd
from transformers import pipeline

def generate_sentiment(ticket):
    """
    Generate sentiment result base on ticket type
    """
    # load model for sentiment analysis
    model = pipeline("sentiment-analysis")

    # insert ticket into model to get sentiment result
    result = model(ticket)

    return result






def main():
    # Test case
    df = pd.read_csv("Data Cleaning/tickets_clean.csv")

    for i in range(5):

        ticket = str(df.iloc[i]["body"])

        result = generate_sentiment(ticket)

        print("-" * 60)

        #print("Ticket ID:", df.iloc[i]["Ticket ID"])

        print("Sentiment:", result[0]["label"])

        print("Confidence:", round(result[0]["score"], 4))

if __name__ == "__main__":
    main()