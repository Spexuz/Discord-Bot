import json
import os

MEMORY_FILE = "memory.json"

# Load all memory from file
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# Save all memory to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Ensure user block exists and return it
def get_user(memory, user_id, username="Unknown"):
    user_id = str(user_id)
    if user_id not in memory:
        memory[user_id] = {
            "name": username,
            "tags": [],
            "facts": [],
            "dumb_count": 0,
            "friend_status": "neutral"
        }
    return memory[user_id]

# Add a fact to the user's memory
def add_fact(memory, user_id, fact):
    user = get_user(memory, user_id)
    if fact not in user["facts"]:
        user["facts"].append(fact)

# Increment a stat
def increment_stat(memory, user_id, stat):
    user = get_user(memory, user_id)
    if stat not in user:
        user[stat] = 0
    user[stat] += 1

# Tag a user
def add_tag(memory, user_id, tag):
    user = get_user(memory, user_id)
    if tag not in user["tags"]:
        user["tags"].append(tag)
