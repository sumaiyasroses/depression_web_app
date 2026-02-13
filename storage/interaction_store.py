# storage/interaction_store.py

from collections import defaultdict
from datetime import datetime

# Stores user interactions
user_interactions = defaultdict(list)

def add_message(user_id, text):
    user_interactions[user_id].append({
        "text": text,
        "time": datetime.now()
    })

def get_user_history(user_id):
    return user_interactions[user_id]
