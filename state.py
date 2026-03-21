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

def calculate_base_stats(grade, personality_type):
    """Calculate starting stats from grade and personality"""
    
    grade_band = Config.GRADE_BANDS.get(grade, Config.GRADE_BANDS)
    personality = Config.PERSONALITY_TYPES.get(personality_type, {})

    # CE — grade band + modifiers
    graded_ce = random.randint(grade_band['ce'][0], grade_band['ce'][1])
    ce = graded_ce + personality.get('ce_mod', 0)

    # Control — midpoint of grade band + modifiers
    graded_control = random.randint(grade_band['control'][0], grade_band['control'][1])
    control = graded_control + personality.get("control_mod", 0)
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