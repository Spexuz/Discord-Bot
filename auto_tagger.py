from memory import get_user, add_tag, increment_stat

# Auto Tagging Logic
# This module updates user memory tags based on message content
# Meant to evolve Jarvis' behavior over time

def auto_tag_user(memory, user_id, message_content):
    """
    Applies or updates memory-based tags based on user message patterns.
    Called once per incoming prompt.
    """
    user = get_user(memory, user_id)
    lowered = message_content.lower()

    # —— Dumb Detection ——
    if "how do i" in lowered or lowered.startswith("how to"):
        increment_stat(memory, user_id, "dumb_count")
        if user.get("dumb_count", 0) >= 3:
            add_tag(memory, user_id, "dumb")
            add_tag(memory, user_id, "annoying")

    # —— Respect Recognition ——
    if any(x in lowered for x in [DATA_SAMPLE_RESPECT]):
        add_tag(memory, user_id, "respectable")

    # —— Chaos Energy Detection ——
    if any(x in lowered for x in ["jarvis shut up", "explode", "malfunction", "crash", "wtf"]):
        add_tag(memory, user_id, "chaotic")

    # —— Gamer Recognition ——
    if "valorant" in lowered or "fps" in lowered or "game" in lowered:
        add_tag(memory, user_id, "gamer")

    # —— Art Affinity ——
    if "draw" in lowered or "sketch" in lowered or "art" in lowered:
        add_tag(memory, user_id, "artist")