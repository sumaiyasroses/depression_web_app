import sqlite3
import random
from datetime import datetime, timedelta
import pytz

DB = "database.db"
USER_ID = 1

messages = [
    "I feel very tired lately",
    "I can't sleep at night",
    "Everything feels exhausting",
    "I don't feel like talking to anyone",
    "Today was okay",
    "I feel very lonely",
    "Nothing seems interesting anymore",
    "I feel stressed with everything",
    "I just want to sleep",
    "I feel a little better today"
]

guidance = [
    "Consider resting and maintaining a healthy routine.",
    "Talking to a trusted friend may help.",
    "Try engaging in relaxing activities.",
    "Take small breaks and focus on self-care."
]

def random_timestamp():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    days_ago = random.randint(0, 30)

    # allow late night behavior
    hour = random.choice([1,2,3,4,5,9,11,14,17,21,23])
    minute = random.randint(0,59)

    dt = now - timedelta(days=days_ago)
    dt = dt.replace(hour=hour, minute=minute)

    return dt.strftime("%Y-%m-%d %H:%M:%S")

conn = sqlite3.connect(DB)
cursor = conn.cursor()

for _ in range(50):

    message = random.choice(messages)

    sentiment = round(random.uniform(20, 80), 2)

    risk = round(random.uniform(30, 85), 2)

    timestamp = random_timestamp()

    g = random.choice(guidance)

    cursor.execute("""
        INSERT INTO interactions
        (user_id, message, sentiment, risk_score, guidance, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (USER_ID, message, sentiment, risk, g, timestamp))

conn.commit()
conn.close()

print("50 realistic interaction records created.")