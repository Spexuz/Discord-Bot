import json
import os

CHAT_HISTORY_FILE = "chat_history.json"

# Load existing chat history from file
def load_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        return {}
    with open(CHAT_HISTORY_FILE, "r") as f:
        return json.load(f)

# Save chat history to disk
def save_chat_history(chat):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat, f, indent=2)

# Append a new message to a user's chat history
def append_message(chat, user_id, message):
    user_id = str(user_id)
    if user_id not in chat:
        chat[user_id] = []
    chat[user_id].append(message)
    chat[user_id] = chat[user_id][-300:]  # Trim for token control
