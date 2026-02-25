import sqlite3
from datetime import datetime, timedelta

DB_NAME = "database.db"


def get_user_activity(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp FROM interactions
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [datetime.fromisoformat(r[0]) for r in rows]


def calculate_late_night_usage(timestamps):
    late_night_count = 0

    for ts in timestamps:
        if 0 <= ts.hour <= 4:
            late_night_count += 1

    if len(timestamps) == 0:
        return 0

    return late_night_count / len(timestamps)


def calculate_daily_frequency(timestamps):
    today = datetime.now().date()
    count = 0

    for ts in timestamps:
        if ts.date() == today:
            count += 1

    return count


def weekly_activity_trend(timestamps):
    today = datetime.now()
    last_week = today - timedelta(days=7)

    recent = 0
    older = 0

    for ts in timestamps:
        if ts >= last_week:
            recent += 1
        else:
            older += 1

    if older == 0:
        return 0

    return (recent - older) / max(older, 1)


def calculate_behavioral_risk(user_id):
    timestamps = get_user_activity(user_id)

    late_night_ratio = calculate_late_night_usage(timestamps)
    daily_freq = calculate_daily_frequency(timestamps)
    weekly_trend = weekly_activity_trend(timestamps)

    risk = 0

    # Late night weight
    if late_night_ratio > 0.3:
        risk += 20

    # High daily usage spike
    if daily_freq > 15:
        risk += 15

    # Sudden drop in activity
    if weekly_trend < -0.5:
        risk += 20

    return min(risk, 50)  # behavioral risk max 50
