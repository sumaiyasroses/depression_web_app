import sqlite3
import random
from datetime import datetime, timedelta
import pytz

DB_NAME = "database.db"
USER_ID = 1

posts = [
    "Feeling exhausted lately.",
    "Can’t sleep again at 2AM.",
    "Why does everything feel heavy?",
    "Trying to stay positive.",
    "Another late night coding.",
    "I miss how things used to be.",
    "Overthinking everything.",
    "Coffee and insomnia."
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

for _ in range(100):
    cursor.execute("""
        INSERT INTO posts (user_id, content, timestamp)
        VALUES (?, ?, ?)
    """, (USER_ID, random.choice(posts), random_timestamp()))

conn.commit()
conn.close()

print("Posts created.")