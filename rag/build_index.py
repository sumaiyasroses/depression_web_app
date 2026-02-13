import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

knowledge_path = "../knowledge"
documents = []

for file in os.listdir(knowledge_path):
    if file.endswith(".txt"):
        with open(os.path.join(knowledge_path, file), "r", encoding="utf-8") as f:
            documents.extend(f.read().split("\n\n"))

embeddings = model.encode(documents)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

with open("documents.pkl", "wb") as f:
    pickle.dump(documents, f)

faiss.write_index(index, "knowledge.index")

print("Knowledge base indexed successfully.")
