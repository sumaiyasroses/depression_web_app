1️⃣ Research Paper Summary
🔹 Paper  Analysis

Title: Suicidal Ideation Detection from Twitter Using ML and DL Models

1. Approach Used in the Paper

Dataset: 49,178 tweets collected using Tweepy API

Preprocessing: NLTK cleaning, stopword removal, stemming, lemmatization

Feature Extraction: CountVectorizer (for ML models), Word Embedding (for DL models)

Machine Learning Models: Logistic Regression, Random Forest, SVC, SGD, Naive Bayes

Deep Learning Models: LSTM, BiLSTM, GRU, BiGRU, CNN-LSTM

Best ML Model: Random Forest (93% accuracy)

Best DL Model: BiLSTM (93.6% accuracy)

2. Technical Pros✅

i. Large dataset (49,000+ tweets) improves generalization.

ii. Comparative study between ML and DL gives strong experimental validation.

iii. Strong preprocessing pipeline improves text classification accuracy.

3. Technical Cons❌

i. High computational cost for DL models (BiLSTM, CNN-LSTM).

ii. Binary classification only — does not detect severity levels.

iii. No real-time web deployment or modular architecture presented.

🔹 How My Project Differs / Improves:

1. My system uses Logistic Regression with TF-IDF for lightweight and faster inference, making it suitable for real-time web deployment.

2. Unlike the paper, my architecture separates detection (ML model) and response generation (RAG + LLM), ensuring modularity and ethical AI responses.

3.My project integrates a Flask web application for real-time interaction instead of only performing offline experiments.]


📌 GitHub Repository Analysis
🔹 GitHub Project Analysis

Title: Depression Detection Using Twitter Data

1. Approach Used in the Repository

Data collected using TWINT (Twitter scraping tool)

Manual dataset construction and labeling

Removal of obvious depression indicators (hashtags)

Balanced dataset (50-50 depressive vs non-depressive)

Focus on content-based classification

Intended integration with federated learning for privacy

Suggestion system to recommend CBT chatbot

2. Technical Pros✅

i. Strong dataset construction methodology

ii. Removed hashtags to prevent keyword bias

iii. Manual review improved label quality

iv. Privacy-aware deployment idea

3. Technical Cons❌

i. No clear model architecture specified

ii. Heavy manual data labeling

iii. Not scalable

🔹 How My Project Differs / Improves

i. My project clearly defines a modular architecture (Flask backend + NLP + ML + RAG + LLM), unlike the repository which focuses mainly on dataset creation.

ii. Instead of relying only on dataset construction, my system integrates a trained model (model.pkl) for real-time prediction.

iii. My project includes knowledge-grounded response generation using a RAG module with Sentence-BERT and FAISS, which improves ethical and explainable AI responses.

REFERENCES
Literature Survey
Haque R., Islam N., Islam M., Ahsan M. M. (2022). A comparative analysis on suicidal ideation detection using nlp, machine, and deep learning. Technologies 10:57. 10.3390/technologies10030057 (https://pmc.ncbi.nlm.nih.gov/articles/PMC12460309/#B41)

Github
https://github.com/swcwang/depression-detection?tab=readme-ov-file#depression-detection-using-twitter-data