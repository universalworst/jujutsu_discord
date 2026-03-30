import json
import os
from config import Config
import random


def default_state(name, discord_id):
    return  {
        "identity": {
            "name": name,
            "discord_id": discord_id,
            "log_channel_id": "",
            "grade": None,
            "age": 25,
            "origin": "",
            "personality_type": "",
            "personality": "",
            "appearance": "",
            "backstory": ""
        },
        "technique": {
            "technique_name": "",
            "core_effects": [],
            "limitations": [],
            "power": 0
        },
        "stats": {
            "health": 100,
            "max_health": 100,
            "injuries": [],
            "cursed_energy": 100,
            "max_cursed_energy": 100,
            "control": 50,
            "stability": 5
        },
        "world_state": {
            "relationships": {},
            "active_npcs": [],
            "absent_npcs": [],
            "known_npcs": [],
            "current_location": "tokyo_jujutsu_high",
            "known_locations": [],
            "missions": {
                "current_mission": None,
                "history": []
            }
        },
        "logs": {
            "chat_log": [],
            "summaries": []
        }
    }

def save_state(state):
    path = os.path.join(Config.SAVE_DIR, f"{state['identity']['discord_id']}.json")
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def load_state(discord_id):
    path = os.path.join(Config.SAVE_DIR, f"{discord_id}.json")
    if not os.path.exists(path):
        return default_state(None, discord_id)
    try:
        with open(path) as f:
            state = json.load(f)
            return ensure_state_defaults(state) # still need to make ensure_state_defaults function
    except (json.JSONDecodeError, KeyError):
        print(f"Warning: Save file for {discord_id} was corrupted. Starting fresh.")
        return default_state(None, discord_id)
    
def ensure_state_defaults(state):
    defaults = default_state(None, None)
    for key, value in defaults.items():
        if key not in state:
            state[key] = value
    return state

def get_all_players():
    files = os.listdir(Config.SAVE_DIR)
    return [f.replace(".json", "") for f in files if f.endswith(".json")]

def calculate_base_stats(grade, personality_type, origin):
    """Calculate starting stats from grade and personality"""
    
    grade_band = Config.GRADE_BANDS.get(grade, Config.GRADE_BANDS)
    personality = Config.PERSONALITY_TYPES.get(personality_type, {})
    origin_mod = Config.ORIGIN_MODIFIERS.get(origin, {})

    # CE — grade band + modifiers
    graded_ce = random.randint(grade_band['ce'][0], grade_band['ce'][1])
    ce = graded_ce + personality.get('ce_mod', 0)

    # Control — midpoint of grade band + modifiers
    graded_control = random.randint(grade_band['control'][0], grade_band['control'][1])
    control = graded_control + personality.get("control_mod", 0) + origin_mod.get("control_mod", 0)
    control = max(1, min(100, control))

    # Stability — baseline from grade + personality modifier
    stability = grade_band["stability_base"] + personality.get("stability_mod", 0)
    stability = max(1, min(10, stability))

    return {
        "max_cursed_energy": ce,
        "cursed_energy": ce,
        "control": control,
        "max_control": 100,
        "stability": stability,
        "max_stability": 10
    }

# ===================================
# SESSIONS
# ===================================

def default_session(channel_id):
    return  {
        "channel_id": channel_id,
        "is_active": False,
        "messages": [],
        "current_location": "",
        "active_npcs": [],
        "absent_npcs": [],
        "session_log": [],
        "summaries": [],
        "players": {}  
}

def save_session(session, channel_id):
    path = os.path.join(Config.SESSION_DIR, f"{channel_id}.json")
    with open(path, "w") as f:
        json.dump(session, f, indent=2)

def load_session(channel_id):
    path = os.path.join(Config.SESSION_DIR, f"{channel_id}.json")
    if not os.path.exists(path):
        return default_session(channel_id)
    try:
        with open(path) as f:
            session = json.load(f)
            return ensure_session_defaults(session)
    except (json.JSONDecodeError, KeyError):
        print(f"Warning: Save file for {channel_id} was corrupted. Starting fresh.")
        return default_session(channel_id)
    
def ensure_session_defaults(session):
    defaults = default_session(None)
    for key, value in defaults.items():
        if key not in session:
            session[key] = value
    return session

def convert_session_to_state(session):
    """Convert session data to a player state format for AI processing"""
    for player_id, player_data in session["players"].items():
        max_cursed_energy = player_data.get("max_cursed_energy")
        control = player_data.get("control")
        stability = player_data.get("stability")
        new_known_npcs = player_data.get("known_npcs")
        discord_id = int(player_id)
        state = load_state(discord_id)
        state["stats"]["max_cursed_energy"] = max_cursed_energy
        state["stats"]["control"] = control
        state["stats"]["stability"] = stability
        known_npcs = state["world_state"]["known_npcs"]
        for npc_id in state["world_state"]["known_npcs"]:
            if npc_id in new_known_npcs:
                if npc_id not in known_npcs:
                    known_npcs.append(npc_id)
        state["world_state"]["known_npcs"] = known_npcs
        save_state(state)