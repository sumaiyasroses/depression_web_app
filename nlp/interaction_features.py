import sqlite3
from datetime import datetime

def get_user_activity(user_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp
        FROM ai_chat
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    timestamps = []

    for r in rows:
        timestamps.append(r[0])

    return timestamps


def calculate_late_night_usage(timestamps):

    if not timestamps:
        return 0

    late = 0

    for ts in timestamps:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

        if dt.hour >= 23 or dt.hour <= 4:
            late += 1

    return late / len(timestamps)


def calculate_behavioral_risk(user_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message
        FROM ai_chat
        WHERE user_id = ?
    """, (user_id,))

    messages = cursor.fetchall()
    conn.close()

    risk = 0

    keywords = [
        "tired",
        "exhausted",
        "sad",
        "alone",
        "lonely",
        "stressed",
        "worthless",
        "empty",
        "hopeless"
    ]

    for m in messages:
        text = m[0].lower()

        for k in keywords:
            if k in text:
                risk += 1

    return min(risk, 40)