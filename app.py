import sqlite3
import joblib

from nlp.analyzer import analyze_text
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db
from storage.interaction_store import add_message, get_user_history
from behavior.behavior_analyzer import calculate_behavioral_risk
from nlp.post_analyzer import analyze_user_posts
from nlp.interaction_features import (
    get_user_activity,
    calculate_late_night_usage,
    calculate_behavioral_risk
)

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model_ai = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

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
        SELECT COUNT(*)
        FROM interactions
        WHERE user_id = ?
    """, (user_id,))

    total_interactions = cursor.fetchone()[0]

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
    if avg_risk < 30:
        risk_level = "Low Risk"

    elif avg_risk < 60:
        risk_level = "Moderate Risk"

    else:
        risk_level = "High Risk"

    if risk_level == "Low Risk":
        analysis_summary = "Your recent interactions show generally stable emotional patterns."
        guidance = "Maintain healthy routines, stay socially connected, and continue positive activities."

    elif risk_level == "Moderate Risk":
        analysis_summary = "Some emotional distress patterns were detected in recent interactions."
        guidance = "Consider taking breaks, improving sleep habits, and talking with supportive friends or family."

    else:
        analysis_summary = "Strong indicators of emotional distress were detected in recent interactions."
        guidance = "Consider reaching out to trusted people or a mental health professional for support."


    cursor.execute("""
        SELECT timestamp, risk_score
        FROM interactions
        WHERE user_id = ?
        ORDER BY timestamp ASC
        """, (user_id,))

    rows = cursor.fetchall()

    dates = [r[0] for r in rows]
    risk_values = [r[1] for r in rows]

    cursor.execute("""
    SELECT timestamp, risk_score
    FROM interactions
    WHERE user_id = ?
    ORDER BY timestamp
""", (user_id,))

    rows = cursor.fetchall()

    dates = []
    risk_values = []

    for row in rows:
        dates.append(row[0])
        risk_values.append(row[1])

    late_night_percent = round(late_night_ratio * 100, 2)
    day_percent = 100 - late_night_percent

    conn.close()


    return render_template(
        "dashboard.html",
        username=session["username"],
        history=history,
        late_night_ratio=round(late_night_ratio * 100, 2),
        behavior_risk=behavior_risk,
        avg_risk=avg_risk,
        risk_level=risk_level,
        analysis_summary=analysis_summary,
        guidance=guidance,
        total_interactions=total_interactions,
        dates=dates,
        risk_values=risk_values,
        late_night_percent=late_night_percent,
        day_percent=day_percent,

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

    post_risk = analyze_user_posts(session["user_id"])

    final_risk = min(risk_score + behavior_risk + post_risk, 100)
    

    guidance = "Practice self-care and consider talking to someone you trust."

    add_message(
        session["user_id"],
        message,
        sentiment,
        final_risk,
        guidance
    )

    return redirect(url_for("dashboard"))


# -------------------------
# CHATS-----------------
# -------------------------
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

    chats = []
    contacts_list = []

    # -----------------------------
    # HANDLE MESSAGE SEND
    # -----------------------------
    if request.method == "POST":

        contact = request.form["contact"]
        message = request.form["message"]

        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

        # Save user message
        cursor.execute("""
            INSERT INTO ai_chat
            (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], contact, "user", message, timestamp))


        # -----------------------------
        # AUTO REPLIES
        # -----------------------------
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


    # -----------------------------
    # LOAD CONTACT LIST
    # -----------------------------
    cursor.execute("""
        SELECT contact_name, message, timestamp
        FROM ai_chat
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (session["user_id"],))

    rows = cursor.fetchall()

    contacts = {}

    for name, message, timestamp in rows:

        if name not in contacts:

            contacts[name] = {
                "last_message": message,
                "timestamp": timestamp
            }

    contacts_list = [
        (name, data["last_message"], data["timestamp"])
        for name, data in contacts.items()
    ]


    # -----------------------------
    # LOAD CHAT MESSAGES
    # -----------------------------
    if contact:

        cursor.execute("""
            SELECT contact_name, sender, message, timestamp
            FROM ai_chat
            WHERE user_id = ? AND contact_name = ?
            ORDER BY timestamp ASC
        """, (session["user_id"], contact))

        chats = cursor.fetchall()


    conn.close()

    return render_template(
        "chats.html",
        contacts=contacts_list,
        chats=chats,
        selected_contact=contact
    )

# -------------------------
# SAFA AI-----------------
# -------------------------


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
    user_id = session["user_id"]

    # Insert first AI message if chat is empty
    cursor.execute("""
        SELECT COUNT(*) FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
    """, (user_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        first_message = "Hi, I'm SAFA. I'm here to listen. How have you been feeling lately?"
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "SAFA", "ai", first_message,
              datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    # Handle user message
    if request.method == "POST":

        message = request.form["message"]
        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

        # ML prediction
        X = vectorizer.transform([message])
        prob = model.predict_proba(X)[0][1]
        risk_score = round(prob * 100, 2)

        behavior_risk = calculate_behavioral_risk(user_id)
        final_risk = min(risk_score + behavior_risk, 100)

        # Save to interactions
        cursor.execute("""
            INSERT INTO interactions (user_id, message, risk_score, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, message, final_risk, timestamp))

        # Save user message
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "SAFA", "user", message, timestamp))

        conn.commit()

        # Fetch last 20 messages
        cursor.execute("""
            SELECT sender, message
            FROM ai_chat
            WHERE user_id=? AND contact_name='SAFA'
            ORDER BY id DESC
            LIMIT 20
        """, (user_id,))
        history = cursor.fetchall()
        history.reverse()

        conversation = ""
        for sender, msg in history:
            if sender == "user":
                conversation += f"User: {msg}\n"
            else:
                conversation += f"SAFA: {msg}\n"

        system_prompt = """
You are SAFA, a compassionate AI mental health assistant.

Rules:
- Be empathetic and supportive
- Keep replies short (1–2 sentences)
- Ask one gentle follow-up question
- Focus on emotional wellbeing
"""

        prompt = system_prompt + "\n" + conversation + "SAFA:"

        # Generate AI reply
        input_ids = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")

        output = model_ai.generate(
            input_ids,
            max_new_tokens=80,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_k=40,
            top_p=0.9,
            temperature=0.7
        )

        reply = tokenizer.decode(
            output[0][input_ids.shape[-1]:],
            skip_special_tokens=True
        ).strip()

        if reply == "":
            reply = "I'm here with you. Can you tell me more about how you're feeling?"

        # Save AI reply
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "SAFA", "ai", reply,
              datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()

    # Fetch full chat
    cursor.execute("""
        SELECT sender, message, timestamp
        FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
        ORDER BY timestamp ASC
    """, (user_id,))

    chats = cursor.fetchall()

    conn.close()

    return render_template("safa_ai.html", messages=chats)

# -------------------------
# SAFA AI CHAT ANALYSIS
# -------------------------

@app.route("/analyze_conversation", methods=["POST"])
def analyze_conversation():

    if "user_id" not in session:
        return redirect(url_for("login"))

    import sqlite3

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
        SELECT message
        FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA' AND sender='user'
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return redirect(url_for("safa_ai"))

    full_text = " ".join([r[0] for r in rows])

    X = vectorizer.transform([full_text])
    prob = model.predict_proba(X)[0][1]

    risk_score = round(prob * 100, 2)

    behavior_risk = calculate_behavioral_risk(user_id)
    post_risk = analyze_user_posts(user_id)

    final_risk = min(risk_score + behavior_risk + post_risk, 100)

    if final_risk > 70:
        level = "High Risk"
        risk_class = "high"
    elif final_risk > 40:
        level = "Moderate Risk"
        risk_class = "moderate"
    else:
        level = "Low Risk"
        risk_class = "low"

    conn.close()

    return render_template(
        "analysis_result.html",
        risk=final_risk,
        level=level,
        risk_class=risk_class
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
