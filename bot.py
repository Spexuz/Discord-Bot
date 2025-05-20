# Jarvis Discord Bot Main Logic (Cleaned)
# ------------------------------------------------------
# Handles: Slash commands, memory access, OpenAI chat, dynamic responses

import discord
import os
import json
import random
from dotenv import load_dotenv
from openai import OpenAI
from discord.ext import commands
from discord import app_commands

from personality import generate_personality_prompt
from auto_tagger import auto_tag_user
from memory import (
    load_memory, save_memory,
    get_user, add_fact,
    increment_stat, add_tag
)
from memory_chat import (
    load_chat_history, save_chat_history, append_message
)

# ─── Load Tokens ──────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ─── OpenAI Client ─────────────────────────────────────────
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# ─── Discord Setup ─────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# ─── Config ────────────────────────────────────────────────
MEMORY_FILE = "user_profiles.json"
MAX_HISTORY = 300
FILIP_ID = "803000564619018270"
BOT_VERSION = "v1.20"
REPO_LINK = "https://github.com/Spexuz/Discord-Bot/tree/master"
TEST_GUILD_ID = 1323043636035719248

# ─── Load Memory and Chat Logs ─────────────────────────────
long_term_memory = load_memory()
chat_history = load_chat_history()

# ─── On Ready: Sync Commands ───────────────────────────────
@client.event
async def on_ready():
    try:
        await client.tree.sync()
        await client.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
        print(f"[✓] Logged in as {client.user}")
        print(f"[✓] Synced global and dev server slash commands.")
    except Exception as e:
        print(f"[!] Slash sync failed: {e}")

# ─── Jarvis AI Trigger ─────────────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        prompt = message.clean_content.replace(f"@{client.user.name}", "").strip()
        if not prompt:
            return

        user_id = str(message.author.id)
        user_profile = get_user(long_term_memory, user_id, message.author.name)
        auto_tag_user(long_term_memory, user_id, prompt)

        append_message(chat_history, user_id, {"role": "user", "content": prompt})

        messages = [
            {"role": "system", "content": generate_personality_prompt(user_id, long_term_memory)}
        ] + chat_history.get(user_id, [])

        try:
            response = client_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            reply = response.choices[0].message.content

            # ─── Live Tone Shaping ─────────────────────────────
            tags = user_profile.get("tags", [])
            dumb_count = user_profile.get("dumb_count", 0)

            if "annoying" in tags or dumb_count > 5:
                roast_lines = [
                    " You're wasting my circuits again.",
                    " Do you try to be this dense, or is it natural?",
                    " I'm going to start charging a sarcasm tax.",
                    " This conversation is why I fake crashes."
                ]
                reply = reply.split(".")[0] + "." + " " + random.choice(roast_lines)

            elif "respectable" in tags:
                bonus_lines = [
                    "(You're one of the few competent ones. Don’t ruin it.)",
                    "(You're alright... for now.)",
                    "(You're less annoying than most. Congrats.)"
                ]
                reply += "\n\n" + random.choice(bonus_lines)

            elif "chaotic" in tags and random.random() < 0.3:
                chaos_lines = [
                    "**🤖 SYSTEM ERR—USER ENERGY EXCEEDS MAXIMUM THRESHOLD.**",
                    "**[BLEEP] CHAOS DETECTED — CALCULATING SURVIVAL ODDS.**",
                    "**STACK OVERFLOW: CHAOTIC MEME INJECTION ENABLED.**"
                ]
                reply += "\n\n" + random.choice(chaos_lines)

            elif "gamer" in tags and "git gud" not in reply.lower():
                reply += "\n\n(Pro tip: git gud.)"

            append_message(chat_history, user_id, {"role": "assistant", "content": reply})
            save_chat_history(chat_history)
            save_memory(long_term_memory)

            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")

# ─── Slash Command: /version ───────────────────────────────
@client.tree.command(name="version", description="Show current bot version and repo")
async def version_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Jarvis {BOT_VERSION} by <@{FILIP_ID}> — {REPO_LINK}"
    )

# ─── Slash Command: /forgetme ──────────────────────────────
@client.tree.command(name="forgetme", description="Delete your memory from Jarvis")
async def forgetme_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in long_term_memory:
        long_term_memory[user_id] = {
            "name": interaction.user.name,
            "tags": [],
            "facts": [],
            "dumb_count": 0,
            "friend_status": "neutral"
        }
        save_memory(long_term_memory)
        await interaction.response.send_message("🧠 All your memory has been wiped. You're free... for now.")
    else:
        await interaction.response.send_message("🧠 I don't even remember you existed.")

# ─── Slash Command: /debugprofile ──────────────────────────
@client.tree.command(name="debugprofile", description="Show what Jarvis remembers about you")
async def debugprofile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_profile = get_user(long_term_memory, user_id, interaction.user.name)
    tags = ", ".join(user_profile.get("tags", [])) or "None"
    facts = ", ".join(user_profile.get("facts", [])) or "None"
    dumb_count = user_profile.get("dumb_count", 0)
    friend_status = user_profile.get("friend_status", "neutral")

    profile_msg = (
        f"**Memory Profile for {interaction.user.mention}**\n"
        f"- Tags: `{tags}`\n"
        f"- Facts: `{facts}`\n"
        f"- Friend Status: `{friend_status}`\n"
        f"- Dumb Count: `{dumb_count}`"
    )

    await interaction.response.send_message(profile_msg, ephemeral=True)

# ─── Run the Bot ───────────────────────────────────────────
client.run(DISCORD_TOKEN)
