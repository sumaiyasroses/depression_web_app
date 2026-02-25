# nlp/analyzer.py

import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.strip()


def detect_keywords(text):
    depression_keywords = [
        "hopeless",
        "worthless",
        "tired",
        "exhausted",
        "empty",
        "alone",
        "sad",
        "crying",
        "suicide",
        "kill myself",
        "no energy",
        "nothing matters",
        "lost interest"
    ]

    detected = []
    for word in depression_keywords:
        if word in text:
            detected.append(word)

    return detected


def analyze_text(text):
    cleaned = clean_text(text)

    # VADER Sentiment
    scores = analyzer.polarity_scores(cleaned)
    compound_score = scores["compound"]

    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Keyword detection
    keywords = detect_keywords(cleaned)

    return sentiment, compound_score