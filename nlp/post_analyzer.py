import nltk
nltk.download('vader_lexicon')
import sqlite3
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

DB_NAME = "database.db"

sia = SentimentIntensityAnalyzer()

def analyze_user_posts(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT content, timestamp FROM posts WHERE user_id = ?", (user_id,))
    posts = cursor.fetchall()
    conn.close()

    if not posts:
        return 0  # No extra risk

    negative_count = 0
    late_night_count = 0

    for content, timestamp in posts:
        sentiment = sia.polarity_scores(content)

        if sentiment["compound"] < -0.5:
            negative_count += 1

        # check late night (00:00 - 04:00)
        hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
        if 0 <= hour <= 4:
            late_night_count += 1

    post_risk = 0

    if negative_count >= 3:
        post_risk += 0.2

    if late_night_count >= 3:
        post_risk += 0.1

    return post_risk