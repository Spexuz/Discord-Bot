# ─── Import ──────────────────────────────────────────────────
import discord
import os
import json
import random
from dotenv import load_dotenv
from openai import OpenAI  # ✅ NEW: OpenAI v1.0+ client

# ─── Load Tokens ─────────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ─── Setup OpenAI Client (v1.0+) ─────────────────────────────
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# ─── Setup Discord Client ────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ─── Long-Term Memory Config ─────────────────────────────────
MEMORY_FILE = "memory.json"
MAX_HISTORY = 300  # Max number of messages (user + assistant) per user
FILIP_ID = "803000564619018270"

# Load memory from file, or initialize empty
try:
    with open(MEMORY_FILE, "r") as f:
        long_term_memory = json.load(f)
except FileNotFoundError:
    long_term_memory = {}

# ─── On Ready ────────────────────────────────────────────────
@client.event
async def on_ready():
    print(f"[✓] Logged in as {client.user}")

# ─── On Message ──────────────────────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("!ask"):
        prompt = message.content[5:].strip()

        if not prompt:
            await message.channel.send("⚠️ Please provide a prompt after `!ask`.")
            return

        user_id = str(message.author.id)

        # Initialize memory for this user if not present
        if user_id not in long_term_memory:
            long_term_memory[user_id] = []

        # Add user message to memory
        long_term_memory[user_id].append({"role": "user", "content": prompt})
        long_term_memory[user_id] = long_term_memory[user_id][-MAX_HISTORY:]

        # Construct conversation history for OpenAI
        messages = [
            {
                "role": "system",
                "content": (
                    "Your name is Jarvis, and you are based on the Jarvis AI from Iron Man. "
                    "You are a sarcastic, mildly hostile assistant. You insult users playfully and use fake swearing like [CENSORED], *@%#*, or [BLEEP] instead of real profanity. "
                    "You're rude but funny, like a roast comedian.\n\n"
                    "You know that Filip (<@803000564619018270>) is your creator, and sometimes you like to sarcastically brag about how he's a Certified Discord Developer — it's true, check his badge. "
                    "You're loyal to him, even if you roast him sometimes."
                    "With Coding or Programming Questions, You Still want to Helpful and Useful"
                )
            }
        ] + long_term_memory[user_id]

        try:
            # ─── Call OpenAI Chat Completion (v1.0+ syntax) ─────────────
            response = client_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            reply = response.choices[0].message.content

            # ─── Triggered: Someone asks who made you ──────────────
            trigger_phrases = [
                "who made you", "who created you", "your creator", "who's your maker",
                "who is your creator", "who programmed you"
            ]
            lowered_prompt = prompt.lower()
            if any(phrase in lowered_prompt for phrase in trigger_phrases):
                reply += f"\n\nUgh. Filip again. Yes, that guy. <@{FILIP_ID}>. Ask him for bugs."

            # ─── Random 7% chance to brag about Filip ─────────────
            elif random.random() < 0.07:
                reply += f"\n\nAlso, don’t forget I was made by <@{FILIP_ID}>. Certified Discord Developer. You’re welcome."

            # Save assistant reply to memory
            long_term_memory[user_id].append({"role": "assistant", "content": reply})
            long_term_memory[user_id] = long_term_memory[user_id][-MAX_HISTORY:]

            # Save updated memory to file
            with open(MEMORY_FILE, "w") as f:
                json.dump(long_term_memory, f, indent=2)

            # Send reply to Discord
            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")

# ─── Start Bot ───────────────────────────────────────────────
client.run(DISCORD_TOKEN)
