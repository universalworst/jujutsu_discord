# ================================
# IMPORTS
# ================================

import json
from config import Config
from data import load_all_lore
from openai import AsyncOpenAI
from utils import parse_llm_json
from state import save_state, save_session

client = AsyncOpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.BASE_URL
)

# ================================
# SCENE TRACKER
# ================================

async def detect_scene(state, narration, lore):
    npc_ids = list(lore.get("npc_profiles", {}).keys())
    absent_npcs = state["world_state"].get("absent_npcs", [])
    active_npcs = state["world_state"].get("active_npcs", [])
    known_npcs = state["world_state"].get("known_npcs", [])
    location_ids = list(lore.get("locations", {}).keys())
    ce_deltas = Config.CE_DELTA
    ce_regen = Config.ACTIVE_REGEN
    current_location = state["world_state"]["current_location"]
    known_locations = state["world_state"]["known_locations"]
    if current_location not in known_locations:
        state["world_state"]["known_locations"].append(current_location)
        save_state(state)

    prompt = f"""
Given the following narration, extract the current scene state.

NARRATION:
{narration}

NPC IDS: {npc_ids}
LOCATION IDS: {location_ids}
PREVIOUSLY ACTIVE NPCS: {active_npcs}
PREVIOUSLY ABSENT NPCS: {absent_npcs}
KNOWN NPCS: {known_npcs}
CE DELTAS: {ce_deltas}
CE REGEN: {ce_regen}

Return ONLY a JSON object - NOT A LIST - with no explanation, preamble, or markdown formatting:
{{
    "active_npcs": ["list of npc_ids physically present in this scene"],
    "absent_npcs": ["list of npc_ids explicitly established as elsewhere or unavailable"],
    "known_npcs": ["list of npc_ids previously shown to be known, plus the npc_ids for any active_npcs that are not already listed as known_npcs"]
    "ce_depleted": "boolean value of true or false based on whether or not the player expended cursed energy during the turn",
    "ce_delta": "if 'ce_depleted' == False, ce_delta is 'none', value 0; if 'ce_depleted' == True; determine if use was minor, moderate, major, or domain expansion, and apply the delta assigned in CE DELTAS above; value must be an integer",
    "ce_restored": "boolean value of true or false based on whether or not the player acted to restore their cursed energy using one of the methods laid out in ce_regen",
    "ce_regen": "if 'ce_regen' == False, ce_regen is 'none', value 0; if 'ce_restored' == True, determine the nature of the restoration (sleep, meditation, brief rest, breathwork, eating) and apply the delta assigned in CE REGEN; value must be an integer",
    "ce_reasoning": "Explanation of whether ce_depleted was true or false and, if true, the level of depletion; value should be a string"
    }}

Rules:
- Only include NPCs physically present in the scene in active_npcs
- If an NPC is merely mentioned but not present, do not include them in active_npcs
- If an NPC is established as absent or unavailable, include them in absent_npcs
- Only use IDs from the provided lists
- Always include ce_reasoning to explain why ce was or was not changed.
"""
    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=800
    )

    content = response.choices[0].message.content.strip()

    try:
        result = parse_llm_json(content)
        print(f"DEBUG detect_scene result: {result}")
        return result
    except json.JSONDecodeError:
        print(f"Warning: scene detection returned malformed JSON: {content}")
        return None
    
def update_scene(state, result):
    state["world_state"]["active_npcs"] = result.get("active_npcs", state["world_state"]["active_npcs"])
    state["world_state"]["absent_npcs"] = result.get("absent_npcs", state["world_state"]["absent_npcs"])
    state["world_state"]["known_npcs"] = result.get("known_npcs", state["world_state"]["known_npcs"])
    ce = state["stats"]["cursed_energy"]
    max_ce = state["stats"]["max_cursed_energy"]
    regen = int(result.get("ce_regen", 0))
    delta = int(result.get("ce_delta", 0))
    new_ce = max(0, min(max_ce, ((ce - delta) + regen + int(max_ce * Config.PASSIVE_REGEN_RATE))))
    state["stats"]["cursed_energy"] = new_ce

# =================================
# SESSION SCENE TRACKER
# =================================

async def detect_scene_session(session, narration, lore):
    npc_ids = list(lore.get("npc_profiles", {}).keys())
    absent_npcs = session.get("absent_npcs", [])
    active_npcs = session.get("active_npcs", [])
    ce_deltas = Config.CE_DELTA
    ce_regen = Config.ACTIVE_REGEN
    session_players = list(session.get("players"))
    location_ids = list(lore.get("locations", {}).keys())
    current_location = session.get("current_location")
    print("Scene detection in process...")

    prompt = f"""
Given the following narration, extract the current scene state and determine cursed energy changes for each player.

NARRATION:
{narration}

NPC IDS: {npc_ids}
LOCATION IDS: {location_ids}
PREVIOUS CURRENT LOCATION: {current_location}
PREVIOUSLY ACTIVE NPCS: {active_npcs}
PREVIOUSLY ABSENT NPCS: {absent_npcs}
PLAYERS: {session_players}
CE DELTAS: {ce_deltas}
CE REGEN: {ce_regen}

Return ONLY a JSON object with no explanation, preamble, or markdown formatting:
{{
    "current_location": "location_id or null if unchanged",
    "active_npcs": ["list of npc_ids physically present in this scene"],
    "absent_npcs": ["list of npc_ids explicitly established as elsewhere or unavailable"],
    "players": {{
        "player_id": {{
            "ce_delta": 0,
            "active_regen": 0,
            "ce_reasoning": "explanation"
        }}
    }}
}}

Rules:
- Only include NPCs physically present in the scene in active_npcs
- If an NPC is merely mentioned but not present, do not include them in active_npcs
- If an NPC is established as absent or unavailable, include them in absent_npcs
- Only use IDs from the provided lists
- Only change locations when the narration explicitly says that this has changed
- Use each player's ID from PLAYERS as the key in the players object
- ce_delta and ce_regen must always be integers
"""
    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=800
    )

    content = response.choices[0].message.content.strip()

    try:
        result = parse_llm_json(content)
        print(f"DEBUG detect_scene result: {result}")
        return result
    except json.JSONDecodeError:
        print(f"Warning: scene detection returned malformed JSON: {content}")
        return None
    
def update_scene_session(session, result):
    if not isinstance(result, dict):
        raise TypeError(f"Expected dict, got {type(result)}")
    session["active_npcs"] = result.get("active_npcs", session["active_npcs"])
    session["absent_npcs"] = result.get("absent_npcs", session["absent_npcs"])
    session["current_location"] = result.get("current_location", session["current_location"])
    for player_id, player_data in session["players"].items():
        player_result = result.get("players", {}).get(str(player_id), {})
        delta = int(player_result.get("ce_delta", 0))
        regen = int(player_result.get("ce_regen", 0))
        ce = player_data.get("cursed_energy")
        max_ce = player_data.get("max_cursed_energy")
        new_ce = max(0, min(max_ce, ((ce - delta) + regen + int(max_ce * Config.PASSIVE_REGEN_RATE))))
        player_data["cursed_energy"] = new_ce
    save_session(session, session["channel_id"])
    print("Scene updated.")