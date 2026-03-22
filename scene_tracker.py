# ================================
# IMPORTS
# ================================

import json
from config import Config
from data import load_all_lore
from openai import OpenAI
from utils import parse_llm_json
from state import save_state

client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.BASE_URL
)

# ================================
# SCENE TRACKER
# ================================

def detect_scene(state, narration, lore):
    npc_ids = list(lore.get("npc_profiles", {}).keys())
    absent_npcs = state["world_state"].get("absent_npcs", [])
    active_npcs = state["world_state"].get("active_npcs", [])
    known_npcs = state["world_state"].get("known_npcs", [])
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
PREVIOUSLY ACTIVE NPCS: {active_npcs}
PREVIOUSLY ABSENT NPCS: {absent_npcs}
KNOWN NPCS: {known_npcs}

Return ONLY a JSON object with no explanation, preamble, or markdown formatting:
{{
    "active_npcs": ["list of npc_ids physically present in this scene"],
    "absent_npcs": ["list of npc_ids explicitly established as elsewhere or unavailable"],
    "known_npcs": ["list of npc_ids previously shown to be known, plus the npc_ids for any active_npcs that are not already listed as known_npcs"]
}}

Rules:
- Only include NPCs physically present in the scene in active_npcs
- If an NPC is merely mentioned but not present, do not include them in active_npcs
- If an NPC is established as absent or unavailable, include them in absent_npcs
- Only use IDs from the provided lists
"""
    response = client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=400
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