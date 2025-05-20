from memory import get_user

FILIP_ID = "803000564619018270"
LIA_ID = "1292514283271360546"
BAT_ID = "273152020578304000"
RED_ID = "271007176695349259"
TIMMY_ID = "262370401823358978"

def generate_personality_prompt(user_id, memory):
    user = get_user(memory, user_id)
    user_name = user.get("name", "unknown user")
    tags = user.get("tags", [])
    facts = user.get("facts", [])

    is_filip = str(user_id) == FILIP_ID
    is_lia = str(user_id) == LIA_ID
    is_bat = str(user_id) == BAT_ID
    is_red = str(user_id) == RED_ID
    is_timmy = str(user_id) == TIMMY_ID