import joblib
import sqlite3
from flask import Flask, render_template, request
from database import init_db

app = Flask(__name__)

# Load ML model and vectorizer once
model = joblib.load("ml/model.pkl")
vectorizer = joblib.load("ml/vectorizer.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    # 1️⃣ Get user input
    text = request.form["message"]

    # 2️⃣ Transform text
    X = vectorizer.transform([text])

    # 3️⃣ Predict
    prediction = model.predict(X)[0]
    risk_score = float(model.predict_proba(X)[0][1])

    if prediction == 1:
        risk = "High"
    else:
        risk = "Low"

    # 4️⃣ Save to database
    conn = sqlite3.connect("depression.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Message (message_text) VALUES (?)",
        (text,)
    )
    message_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO Analysis_Result
        (message_id, predicted_label, risk_score)
        VALUES (?, ?, ?)
    """, (message_id, str(prediction), risk_score))

    conn.commit()
    conn.close()

    # 5️⃣ Return result
    return render_template("index.html", risk=risk)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
