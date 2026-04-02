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
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_CLIENT = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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
    from datetime import datetime, timedelta

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # Total interactions
    cursor.execute("SELECT COUNT(*) FROM interactions WHERE user_id = ?", (user_id,))
    total_interactions = cursor.fetchone()[0]

    # Overall avg risk
    cursor.execute("SELECT AVG(risk_score) FROM interactions WHERE user_id = ?", (user_id,))
    avg_risk = round(cursor.fetchone()[0] or 0, 2)

    # Today avg risk
    cursor.execute("""
        SELECT AVG(risk_score) FROM interactions
        WHERE user_id = ? AND DATE(timestamp) = ?
    """, (user_id, today_str))
    today_risk = round(cursor.fetchone()[0] or 0, 2)

    # Last 7 days avg risk
    cursor.execute("""
        SELECT AVG(risk_score) FROM interactions
        WHERE user_id = ? AND DATE(timestamp) >= ?
    """, (user_id, week_ago))
    week_risk = round(cursor.fetchone()[0] or 0, 2)

    # Last 30 days avg risk
    cursor.execute("""
        SELECT AVG(risk_score) FROM interactions
        WHERE user_id = ? AND DATE(timestamp) >= ?
    """, (user_id, month_ago))
    month_risk = round(cursor.fetchone()[0] or 0, 2)

    def get_risk_level(score):
        if score < 30:
            return "Low Risk"
        elif score < 60:
            return "Moderate Risk"
        else:
            return "High Risk"

    def get_summary_guidance(level):
        if level == "Low Risk":
            return (
                "Emotional patterns look stable.",
                "Maintain healthy routines and stay socially connected."
            )
        elif level == "Moderate Risk":
            return (
                "Some emotional distress patterns detected.",
                "Take breaks, improve sleep, and talk to supportive people."
            )
        else:
            return (
                "Strong indicators of emotional distress detected.",
                "Consider reaching out to a trusted person or mental health professional."
            )

    risk_level = get_risk_level(avg_risk)
    analysis_summary, guidance = get_summary_guidance(risk_level)

    today_level = get_risk_level(today_risk)
    week_level  = get_risk_level(week_risk)
    month_level = get_risk_level(month_risk)

    # Chart data — grouped by date segments
    cursor.execute("""
        SELECT DATE(timestamp) as day, AVG(risk_score)
        FROM interactions
        WHERE user_id = ?
        GROUP BY day
        ORDER BY day ASC
    """, (user_id,))
    rows = cursor.fetchall()
    dates       = [r[0] for r in rows]
    risk_values = [round(r[1], 2) for r in rows]

    late_night_percent = round(late_night_ratio * 100, 2)
    day_percent = 100 - late_night_percent

    # SAFA analysis — last 3 entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safa_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, risk_score REAL,
            risk_level TEXT, summary TEXT,
            guidance TEXT, timestamp TEXT
        )
    """)
    cursor.execute("""
        SELECT risk_score, risk_level, summary, guidance, timestamp
        FROM safa_analysis
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 3
    """, (user_id,))
    safa_rows = cursor.fetchall()

    # Latest single entry (for existing references)
    safa_risk     = round(safa_rows[0][0], 2) if safa_rows else None
    safa_level    = safa_rows[0][1]            if safa_rows else None
    safa_summary  = safa_rows[0][2]            if safa_rows else None
    safa_guidance = safa_rows[0][3]            if safa_rows else None

    # Recent list for new UI
    recent_safa = []
    for row in safa_rows:
        recent_safa.append({
            "risk_score": round(row[0], 2),
            "risk_level": row[1],
            "summary":    row[2],
            "guidance":   row[3],
            "timestamp":  row[4]
        })

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
        safa_risk=safa_risk,
        safa_level=safa_level,
        safa_summary=safa_summary,
        safa_guidance=safa_guidance,
        recent_safa=recent_safa,
        today_risk=today_risk,
        today_level=today_level,
        week_risk=week_risk,
        week_level=week_level,
        month_risk=month_risk,
        month_level=month_level,
    )

# -------------------------
# ANALYZE 
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
# SAFA AI REPLY------------
# -------------------------

def get_safa_reply(history):
    system_prompt = """You are SAFA, a warm and empathetic AI mental-health companion.
Your rules:
- Make the user feel heard and safe
- Ask ONE thoughtful follow-up question per reply based on what they just said
- Keep replies SHORT (2-3 sentences max)
- Never repeat the same question or phrase from earlier in the conversation
- Do NOT diagnose or give medical advice
- If distress seems severe, gently suggest speaking with a professional
"""
    messages = [{"role": "system", "content": system_prompt}] + history

    response = GROQ_CLIENT.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ← change this
        messages=messages,
        max_tokens=200,
        temperature=0.8,
        timeout=30  

    )
    return response.choices[0].message.content.strip()



# -------------------------
# GET SAFA ANALYSIS--------
# -------------------------
def get_safa_analysis(conversation_text):
    import json
    prompt = f"""Analyse this mental health support conversation and return ONLY a JSON object with these exact keys:
- "risk_level": one of "High Risk", "Moderate Risk", or "Low Risk"
- "risk_score": a number between 0 and 100
- "summary": 1-2 sentences describing the emotional patterns you observed
- "guidance": 1-2 sentences of supportive actionable advice for this person

Conversation:
{conversation_text}

Return ONLY the JSON object. No explanation, no markdown, no extra text."""

    for attempt in range(3):  # retry up to 3 times
        try:
            response = GROQ_CLIENT.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
                timeout=30
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[Analysis attempt {attempt+1} failed] {e}")
            if attempt == 2:
                raise

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

    ist      = pytz.timezone("Asia/Kolkata")
    user_id  = session["user_id"]

    # ── Insert opening message if chat is completely empty ──────────────────
    cursor.execute("""
        SELECT COUNT(*) FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
    """, (user_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        opening = "Hi, I'm SAFA 🌿 I'm here to listen without judgment. How have you been feeling lately?"
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, 'SAFA', 'ai', ?, ?)
        """, (user_id, opening, datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    # ── Handle new user message ─────────────────────────────────────────────
    if request.method == "POST":

        user_message = request.form["message"].strip()
        if not user_message:
            conn.close()
            return redirect(url_for("safa_ai"))

        now_str = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

        # ML risk scoring (kept from original)
        X          = vectorizer.transform([user_message])
        prob       = model.predict_proba(X)[0][1]
        risk_score = round(prob * 100, 2)

        behavior_risk = calculate_behavioral_risk(user_id)
        final_risk    = min(risk_score + behavior_risk, 100)

        cursor.execute("""
            INSERT INTO interactions (user_id, message, risk_score, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, user_message, final_risk, now_str))

        # Save user message
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, 'SAFA', 'user', ?, ?)
        """, (user_id, user_message, now_str))
        conn.commit()

        # ── Build conversation history for Claude ───────────────────────────
        cursor.execute("""
            SELECT sender, message FROM ai_chat
            WHERE user_id=? AND contact_name='SAFA'
            ORDER BY id ASC
        """, (user_id,))
        rows = cursor.fetchall()

        # Map "ai" → "assistant" for Anthropic API
        claude_history = []
        for sender, msg in rows:
            role = "assistant" if sender == "ai" else "user"
            # Merge consecutive same-role messages (API requires alternating)
            if claude_history and claude_history[-1]["role"] == role:
                claude_history[-1]["content"] += "\n" + msg
            else:
                claude_history.append({"role": role, "content": msg})

        # ── Get Claude reply ────────────────────────────────────────────────
        try:
            reply = get_safa_reply(claude_history)
        except Exception as e:
            reply = "I'm here with you. Could you tell me a little more about what you're experiencing?"
            print(f"[SAFA AI error] {e}")

        # Save AI reply
        cursor.execute("""
            INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
            VALUES (?, 'SAFA', 'ai', ?, ?)
        """, (user_id, reply, datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    # ── Fetch full chat to render ───────────────────────────────────────────
    cursor.execute("""
        SELECT sender, message, timestamp
        FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
        ORDER BY timestamp ASC
    """, (user_id,))
    chats = cursor.fetchall()

    conn.close()
    return render_template("safa_ai.html", chats=chats)


# -------------------------
# SAFA CHAT CLEAR HISTORY--
# -------------------------

@app.route("/safa_ai/new", methods=["GET"])
def safa_ai_new():

    if "user_id" not in session:
        return redirect(url_for("login"))

    import sqlite3

    conn   = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
    """, (session["user_id"],))
    conn.commit()
    conn.close()

    return redirect(url_for("safa_ai"))



# -------------------------
# SAFA ANALYSIS-------------
# -------------------------
@app.route("/analyze_conversation", methods=["POST"])
def analyze_conversation():

    if "user_id" not in session:
        return redirect(url_for("login"))

    import sqlite3
    from datetime import datetime
    import pytz

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    user_id = session["user_id"]
    ist = pytz.timezone("Asia/Kolkata")

    # Get full conversation
    cursor.execute("""
        SELECT sender, message FROM ai_chat
        WHERE user_id=? AND contact_name='SAFA'
        ORDER BY id ASC
    """, (user_id,))
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return redirect(url_for("safa_ai"))

    # Build readable text for Claude
    conversation_text = ""
    for sender, msg in rows:
        label = "SAFA" if sender == "ai" else "User"
        conversation_text += f"{label}: {msg}\n"

    # Claude analyses it
    try:
        analysis  = get_safa_analysis(conversation_text)
        level     = analysis.get("risk_level", "Low Risk")
        risk      = float(analysis.get("risk_score", 20))
        summary   = analysis.get("summary", "No significant patterns detected.")
        guidance  = analysis.get("guidance", "Continue practising self-care.")
    except Exception as e:
        import traceback
        print(f"[Analysis error FULL]")
        traceback.print_exc()
        level, risk, summary, guidance = "Low Risk", 20.0, "Analysis unavailable.", "Take care of yourself."
    
    risk_class = "high" if "High" in level else ("moderate" if "Moderate" in level else "low")
    now_str = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

    # Save to interactions
    cursor.execute("""
        INSERT INTO interactions (user_id, message, risk_score, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, "[SAFA Analysis]", risk, now_str))

    # Save to safa_analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safa_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, risk_score REAL,
            risk_level TEXT, summary TEXT,
            guidance TEXT, timestamp TEXT
        )
    """)
    cursor.execute("DELETE FROM safa_analysis WHERE user_id=?", (user_id,))
    cursor.execute("""
        INSERT INTO safa_analysis (user_id, risk_score, risk_level, summary, guidance, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, risk, level, summary, guidance, now_str))

    conn.commit()
    conn.close()

    return render_template(
        "analysis_result.html",
        risk=round(risk, 2),
        level=level,
        risk_class=risk_class,
        summary=summary,
        guidance=guidance
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
