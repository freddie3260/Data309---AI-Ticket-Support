import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_sentiment_model():
    """Load Model"""
    return pipeline("sentiment-analysis")


def generate_sentiment(ticket):
    """
    Generate sentiment result base on ticket type
    """
    # load model for sentiment analysis
    model = load_sentiment_model()

    # insert ticket into model to get sentiment result
    result = model(ticket)

    return result


def main():
    # Test case
    import pandas as pd
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