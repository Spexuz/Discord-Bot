import os

# ─── Jarvis Code Indexer ─────────────────────────────────────────
# Scans .py files in project directory and creates searchable chunks

CODE_DIRECTORY = "."  # Root of your project
CHUNK_SIZE = 600  # Characters per chunk
ALLOWED_FILES = ["bot.py", "memory.py", "personality.py", "auto_tagger.py", "memory_chat.py"]

# Load and chunk all readable .py files

def load_code_chunks():
    chunks = []

    for filename in os.listdir(CODE_DIRECTORY):
        if not filename.endswith(".py") or filename not in ALLOWED_FILES:
            continue

        try:
            with open(os.path.join(CODE_DIRECTORY, filename), "r", encoding="utf-8") as f:
                code = f.read()

            for i in range(0, len(code), CHUNK_SIZE):
                chunk = code[i:i+CHUNK_SIZE]
                chunks.append({
                    "file": filename,
                    "code": chunk
                })
        except Exception as e:
            print(f"[WARN] Could not read {filename}: {e}")

    return chunks
