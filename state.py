import json
import os
from config import Config


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