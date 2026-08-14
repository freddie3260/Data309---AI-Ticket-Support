import pandas as pd
from transformers import pipeline

df = pd.read_csv("./customer_support_tickets.csv")

sentiment = pipeline("sentiment-analysis")

for i in range(5):

    ticket = str(df.iloc[i]["body"])

    result = sentiment(ticket)

    print("-" * 60)

    #print("Ticket ID:", df.iloc[i]["Ticket ID"])

    print("Sentiment:", result[0]["label"])

    print("Confidence:", round(result[0]["score"], 4))