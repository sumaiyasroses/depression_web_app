# nlp/interaction_features.py

from nlp.analyzer import analyze_text

def extract_features(history):
    sentiments = []
    scores = []

    for item in history:
        sentiment, score = analyze_text(item["text"])
        sentiments.append(sentiment)
        scores.append(score)

    avg_score = sum(scores) / len(scores)
    negative_count = sentiments.count("Negative")

    features = {
        "avg_sentiment_score": avg_score,
        "negative_ratio": negative_count / len(sentiments),
        "message_count": len(history)
    }

    return features
