# ─── Import ─────────────────────────────────────────────────
import discord
import os
import json
import random
from dotenv import load_dotenv
from openai import OpenAI
from discord.ext import commands
from discord import app_commands
from personality import generate_personality_prompt
from memory import (
    load_memory, save_memory,
    get_user, add_fact,
    increment_stat, add_tag
)

# ─── Load Tokens ──────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ─── Setup OpenAI Client ──────────────────────────────────
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# ─── Discord Setup ────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# ─── Config ────────────────────────────────────────────────
MEMORY_FILE = "memory.json"
MAX_HISTORY = 300
FILIP_ID = "803000564619018270"
BOT_VERSION = "v1.20"
REPO_LINK = "https://github.com/Spexuz/Discord-Bot/tree/master"
TEST_GUILD_ID = 1323043636035719248  # Dev server for instant sync

# ─── Load/Init Memory ─────────────────────────────────────
try:
    with open(MEMORY_FILE, "r") as f:
        long_term_memory = json.load(f)
except FileNotFoundError:
    long_term_memory = {}

# ─── On Ready ─────────────────────────────────────────────
@client.event
async def on_ready():
    try:
        # Global + Dev Guild Sync
        await client.tree.sync()
        await client.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))

        print(f"[✓] Logged in as {client.user}")
        print(f"[✓] Synced global and dev server slash commands.")
    except Exception as e:
        print(f"[!] Failed to sync slash commands: {e}")

# ─── Mention-Triggered Jarvis AI ─────────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond if the bot is mentioned directly
    if client.user in message.mentions:
        prompt = message.clean_content.replace(f"@{client.user.name}", "").strip()
        if not prompt:
            return

        user_id = str(message.author.id)

        # Load memory profile (Step 1.2.1)
        user_profile = get_user(long_term_memory, user_id, message.author.name)

        if user_id not in long_term_memory:
            long_term_memory[user_id] = []

        long_term_memory[user_id].append({"role": "user", "content": prompt})
        long_term_memory[user_id] = long_term_memory[user_id][-MAX_HISTORY:]

        messages = [
                       {
                           "role": "system",
                           "content": generate_personality_prompt(user_id, long_term_memory)
                       }
                   ] + long_term_memory[user_id]

        try:
            response = client_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            reply = response.choices[0].message.content

            lowered_prompt = prompt.lower()
            if any(x in lowered_prompt for x in ["who made you", "your creator", "who created you"]):
                reply += f"\n\nUgh. Filip again. Yes, <@{FILIP_ID}>. Ask him for bugs."
            elif random.random() < 0.07:
                reply += f"\n\nAlso, don’t forget I was made by <@{FILIP_ID}>. Certified Discord Developer. You’re welcome."

            long_term_memory[user_id].append({"role": "assistant", "content": reply})
            long_term_memory[user_id] = long_term_memory[user_id][-MAX_HISTORY:]

            # 🧠 Save user profile changes (facts, tags, dumb count, etc.)
            save_memory(long_term_memory)

            # 💬 Send reply back to user
            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")

# ─── /version Slash Command (Global) ──────────────────────────
@client.tree.command(name="version", description="Show current bot version and repo")
async def version_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Jarvis {BOT_VERSION} by <@{FILIP_ID}> — {REPO_LINK}"
    )

# ─── /forgetme Slash Command (Global) ─────────────────────────
@client.tree.command(name="forgetme", description="Delete your memory from Jarvis")
async def forgetme_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id in long_term_memory:
        long_term_memory[user_id] = []
        with open(MEMORY_FILE, "w") as f:
            json.dump(long_term_memory, f, indent=2)
        await interaction.response.send_message("🧠 All your memory has been wiped. You're free... for now.")
    else:
        await interaction.response.send_message("🧠 I don't even remember you existed.")

# ─── Run Bot ──────────────────────────────────────
client.run(DISCORD_TOKEN)
