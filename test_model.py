import joblib

model = joblib.load("ml/model.pkl")
vectorizer = joblib.load("ml/vectorizer.pkl")

test_text = ["I feel tired all the time and I don't enjoy anything anymore"]

X = vectorizer.transform(test_text)

prediction = model.predict(X)

print("Input:", test_text[0])
print("Prediction:", prediction[0])
