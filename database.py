import sqlite3

def init_db():
    conn = sqlite3.connect("depression.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Message (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Analysis_Result (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        predicted_label TEXT,
        risk_score FLOAT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES Message(message_id)
    )
    """)

    conn.commit()
    conn.close()
