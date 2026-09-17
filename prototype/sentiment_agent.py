import streamlit as st
import torch
import os
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

@st.cache_resource
def load_sentiment_model():
    """Load Model"""
    device = 0 if torch.cuda.is_available() else -1

    model_args = {
        "task": "sentiment-analysis",
        "device": device
    }

    if HF_TOKEN:
        model_args["token"] = HF_TOKEN

    return pipeline(**model_args)

def generate_sentiment(ticket):
    """
    Generate sentiment result base on ticket type
    """
    # load model for sentiment analysis
    model = load_sentiment_model()

    # insert ticket into model to get sentiment result
    result = model(ticket)

    # change all other sentiment to non-negative if they are not negative
    if result[0]["label"] == "NEGATIVE":
        result[0]["label"] = "NEGATIVE"
    else:
        result[0]["label"] = "NON-NEGATIVE"

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