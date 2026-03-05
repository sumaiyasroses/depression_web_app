import sqlite3

def add_message(sender, text):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, text) VALUES (?, ?)", (sender, text))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    import sqlite3
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message,sentiment, risk_score, guidance, timestamp
        FROM interactions
        WHERE user_id = ?
        ORDER BY timestamp ASC
    """, (user_id,))

    history = cursor.fetchall()
    conn.close()
    return history

def save_risk(score):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO risk_scores (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()