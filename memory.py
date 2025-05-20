import json
import os

MEMORY_FILE = "user_profiles.json"

# Load all memory from file (or return empty if it doesn't exist)
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# Save all memory to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Ensure a user block exists in memory and return it
def get_user(memory, user_id, username="Unknown"):
    user_id = str(user_id)

    # PATCH: If the stored entry is a chat history list, replace it
    if isinstance(memory.get(user_id), list):
        memory[user_id] = {
            "name": username,
            "tags": [],
            "facts": [],
            "dumb_count": 0,
            "friend_status": "neutral"
        }

    if user_id not in memory:
        memory[user_id] = {
            "name": username,
            "tags": [],
            "facts": [],
            "dumb_count": 0,
            "friend_status": "neutral"
        }

    return memory[user_id]

# Add a fact to a user's memory
def add_fact(memory, user_id, fact):
    user = get_user(memory, user_id)
    if fact not in user["facts"]:
        user["facts"].append(fact)

# Increment a stat like 'dumb_count'
def increment_stat(memory, user_id, stat):
    user = get_user(memory, user_id)
    if stat not in user:
        user[stat] = 0
    user[stat] += 1

# Add a tag to the user's memory (no duplicates)
def add_tag(memory, user_id, tag):
    user = get_user(memory, user_id)
    if tag not in user["tags"]:
        user["tags"].append(tag)