from openai import OpenAI
from code_indexer import load_code_chunks
import os
import random

from dotenv import load_dotenv
load_dotenv()

# ─── Jarvis Code Analyzer ─────────────────────────────────────
# Matches question to relevant code chunks and analyzes behavior

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CODE_CHUNKS = load_code_chunks()

# Analyze a natural language question against source code

def analyze_code(question):
    # Match relevant chunks
    context_chunks = []
    for chunk in CODE_CHUNKS:
        if any(word in chunk["code"].lower() for word in question.lower().split()):
            context_chunks.append(chunk)
        if len(context_chunks) >= 3:
            break

    if not context_chunks:
        return "I searched my files and found nothing relevant. Either I'm flawless, or you're asking nonsense."

    context_text = "\n\n".join(
        f"# From {c['file']}\n{c['code']}" for c in context_chunks
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are Jarvis, a sarcastic but capable AI reflecting on your own code.\n"
                "You don't hallucinate. You only answer based on the code you were shown.\n"
                "Be blunt. Be clever. Be brutally honest about flaws or logic."
            )
        },
        {
            "role": "user",
            "content": f"User asked: {question}\n\nHere is your code context:\n\n{context_text}\n\nExplain the relevant logic and flaws."
        }
    ]

    response = client_openai.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content.strip()
