import sqlite3
import joblib

from nlp.analyzer import analyze_text
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db
from storage.interaction_store import add_message, get_user_history
from behavior.behavior_analyzer import calculate_behavioral_risk
from nlp.interaction_features import extract_features

model = joblib.load("ml/model.pkl")
vectorizer = joblib.load("ml/vectorizer.pkl")

app = Flask(__name__)
app.secret_key = "super_secret_key"  # change this in production
DB_NAME = "database.db"


# -------------------------
# HOME ROUTE
# -------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            return "Username already exists"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("dashboard"))

        return "Invalid credentials"

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------
# DASHBOARD
# -------------------------
from behavior.behavior_analyzer import (
    calculate_behavioral_risk,
    calculate_late_night_usage,
    get_user_activity
)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    history = get_user_history(user_id)
    

    timestamps = get_user_activity(user_id)
    late_night_ratio = calculate_late_night_usage(timestamps)
    behavior_risk = calculate_behavioral_risk(user_id)

    import sqlite3
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM interactions
        WHERE user_id = ?
    """, (user_id,))

    avg_risk = cursor.fetchone()[0]

    if avg_risk:
        avg_risk = round(avg_risk, 2)
    else:
        avg_risk = 0

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        history=history,
        late_night_ratio=round(late_night_ratio * 100, 2),
        behavior_risk=behavior_risk,
        avg_risk=avg_risk

    )



# -------------------------
# ANALYZE (example placeholder)
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    if "user_id" not in session:
        return redirect(url_for("login"))

    message = request.form["message"]

    # Sentiment + features
    sentiment, _ = analyze_text(message)

    # ML prediction
    X = vectorizer.transform([message])
    prob = model.predict_proba(X)[0][1]

    risk_score = round(prob * 100, 2)

    behavior_risk = calculate_behavioral_risk(session["user_id"])

    final_risk = min(risk_score + behavior_risk, 100)
    

    guidance = "Practice self-care and consider talking to someone you trust."

    add_message(
        session["user_id"],
        message,
        sentiment,
        final_risk,
        guidance
    )

    return redirect(url_for("dashboard"))


@app.route("/chats", methods=["GET", "POST"])
def chats():
    if "user_id" not in session:
        return redirect(url_for("login"))

    import sqlite3
    from datetime import datetime
    import pytz
    import random

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    ist = pytz.timezone("Asia/Kolkata")
    contact = request.args.get("contact")

    if request.method == "POST":
        contact = request.form["contact"]
        message = request.form["message"]
        user_msg = message.lower()
        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        if "pm" in user_msg or "am" in user_msg:
            reply = "Thanks for clarifying the time 😊 What’s on your mind?"
        elif "hi" in user_msg:
            reply = "Hey. How are you feeling today?"
        else:
             reply = "Can you tell me a bit more about that?"


        # Save user message
        cursor.execute("""
            INSERT INTO ai_chat 
            (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], contact, "user", message, timestamp))

        auto_replies = {
            "Aisha": [
                "Are you okay?",
                "You sound different today...",
                "Did something happen?",
                "I'm here if you want to talk ❤️"
            ],
            "Rahul": [
                "Bro you good?",
                "Why so quiet lately?",
                "Call me if you need.",
                "Don't overthink too much."
            ],
            "Sara": [
                "Did you eat?",
                "Why are you awake this late?",
                "Take care of your health.",
                "I am praying for you."
            ]
        }

        if contact in auto_replies:
            reply = random.choice(auto_replies[contact])
            reply_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO ai_chat 
                (user_id, contact_name, sender, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session["user_id"], contact, "contact", reply, reply_time))

        conn.commit()

    if contact:
        cursor.execute("""
            SELECT contact_name, sender, message, timestamp
            FROM ai_chat
            WHERE user_id = ? AND contact_name = ?
            ORDER BY timestamp ASC
        """, (session["user_id"], contact))
        chats = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT DISTINCT contact_name
            FROM ai_chat
            WHERE user_id = ?
        """, (session["user_id"],))
        chats = cursor.fetchall()

    conn.close()
    return render_template("chats.html", chats=chats, selected_contact=contact)



@app.route("/safa_ai", methods=["GET", "POST"])
def safa_ai():
    if "user_id" not in session:
        return redirect(url_for("login"))

    import sqlite3
    from datetime import datetime
    import pytz

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    ist = pytz.timezone("Asia/Kolkata")

    if request.method == "POST":
        message = request.form["message"]
        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], "SAFA", "user", message, timestamp))

        lower_msg = message.lower()

        if "sad" in lower_msg:
            reply = "What has been making you feel sad recently?"
        elif "anxious" in lower_msg:
            reply = "What usually triggers your anxiety?"
        elif "angry" in lower_msg:
            reply = "What happened that made you feel angry?"
        elif "tired" in lower_msg:
            reply = "Have you been resting properly lately?"
        elif lower_msg in ["no", "i dont know", "idk"]:
            reply = "That’s okay. Sometimes feelings are hard to explain. Can you describe how your day felt?"
        else:
            reply = "Can you tell me a little more about that?"

        reply_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], "SAFA", "ai", reply, reply_time))

        conn.commit()

    cursor.execute("""
        SELECT sender, message, timestamp
        FROM ai_chat
        WHERE user_id = ? AND contact_name = 'SAFA'
        ORDER BY timestamp ASC
    """, (session["user_id"],))

    chats = cursor.fetchall()
    conn.close()

    return render_template("safa_ai.html", chats=chats)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
