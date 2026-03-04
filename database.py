import sqlite3

def init_db():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        text TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score REAL
    )
    """)

    conn.commit()
    conn.close()