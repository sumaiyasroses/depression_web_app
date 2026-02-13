import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

# Get absolute path of this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Correct paths
index_path = os.path.join(BASE_DIR, "knowledge.index")
docs_path = os.path.join(BASE_DIR, "documents.pkl")

# Load FAISS index
index = faiss.read_index(index_path)

# Load documents
with open(docs_path, "rb") as f:
    documents = pickle.load(f)


def retrieve_info(query, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        results.append(documents[idx])

    return results
