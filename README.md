
# AI-Driven Depression Detection Platform

A web-based platform that leverages AI to assess potential depression risk from user social interaction data. It combines NLP, Machine Learning, and a RAG (Retrieval-Augmented Generation) module to provide safe, knowledge-backed insights.

**Features**

Message Analysis – Extracts sentiment, emotion, and behavioral cues using NLP.

Depression Risk Prediction – ML models (Logistic Regression / Random Forest) predict risk levels based on interaction patterns.

Knowledge-Backed Advice – RAG module retrieves verified mental health guidelines and coping strategies.

User History Tracking – Stores and analyzes previous interactions for improved personalization.

Real-Time Web Interface – Simple Flask-based frontend for interactive analysis.


# Tech Stack

**Backend**: Python, Flask

**NLP**: VADER Sentiment Analysis, custom interaction features

**ML Models**: Logistic Regression, Random Forest

**RAG Module**: Sentence-BERT embeddings + FAISS

**Frontend**: HTML, CSS, JS

**Database**: SQLite3


# Usage

Clone the repo

Install dependencies: pip install -r requirements.txt

Run: python app.py

Open http://localhost:5000 in your browser
