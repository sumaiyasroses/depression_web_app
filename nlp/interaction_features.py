# nlp/interaction_features.py

from nlp.analyzer import analyze_text

# nlp/interaction_features.py

def extract_features(history):
    sentiments = []
    scores = []
    late_night_count = 0

    for row in history:
        message, sentiment, risk_score, guidance, timestamp = row

        scores.append(risk_score)

        if sentiment == "Negative":
            sentiments.append(1)
        else:
            sentiments.append(0)

        # Check late night (after 11 PM)
        hour = int(timestamp.split(" ")[1].split(":")[0])
        if hour >= 23 or hour <= 4:
            late_night_count += 1

    if len(scores) == 0:
        return {
            "avg_risk_score": 0,
            "negative_ratio": 0,
            "message_count": 0,
            "late_night_ratio": 0
        }

    features = {
        "avg_risk_score": sum(scores) / len(scores),
        "negative_ratio": sum(sentiments) / len(sentiments),
        "message_count": len(history),
        "late_night_ratio": late_night_count / len(history)
    }

    return features
