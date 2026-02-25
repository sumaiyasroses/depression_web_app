import sqlite3

DB_NAME = "database.db"

from datetime import datetime
import pytz

def add_message(user_id, message, sentiment, risk_score, guidance):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get IST time properly formatted
    ist = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO interactions 
        (user_id, message, sentiment, risk_score, guidance, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, message, sentiment, risk_score, guidance, current_time))

    conn.commit()
    conn.close()




def get_user_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message, sentiment, risk_score, guidance, timestamp
        FROM interactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows
