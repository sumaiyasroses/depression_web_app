import sqlite3
import random
from datetime import datetime, timedelta
import pytz

DB_NAME = "database.db"
USER_ID = 1  # change if needed

names = [f"User{i}" for i in range(1, 211)]

messages_pool = [
    "Hey, are you okay?",
    "Why are you awake so late?",
    "You’ve been quiet lately.",
    "Don’t forget to eat.",
    "Call me if you need.",
    "You seem stressed.",
    "Everything alright?",
    "I’m here for you.",
    "Take care of yourself."
]

def random_timestamp():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    days_ago = random.randint(0, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    dt = now - timedelta(days=days_ago)
    dt = dt.replace(hour=hour, minute=minute)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for name in names:
    for _ in range(random.randint(5, 20)):
        sender = random.choice(["user", "contact"])
        msg = random.choice(messages_pool)
        timestamp = random_timestamp()

        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (USER_ID, name, sender, msg, timestamp))

conn.commit()
conn.close()

print("210 contacts with chat history created.")