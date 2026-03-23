# ========================================
# IMPORTS
# ========================================

import json
from config import Config
from openai import AsyncOpenAI
from utils import parse_llm_json
from data import load_all_lore

client = AsyncOpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.BASE_URL
)

# ========================================
# RELATIONSHIP HELPERS
# ========================================

def default_relationship_entry():
    return {
        "type": ["unknown"],
        "trust": 50,
        "respect": 50,
        "affection": 30,
        "tension": 20,
        "emotional_tone": "neutral",
        "background": "",
        "shared_history": [],
        "unresolved_threads": []
    }

# ========================================
# RELATIONSHIP SEEDING
# ========================================

async def seed_relationships(state, seed):
    backstory = state["identity"].get("backstory", "")
    personality = state["identity"].get("personality", "")
    if not backstory:
        return

    npc_ids = list(load_all_lore().get("npc_profiles", {}).keys())

    prompt = f"""
Given this character's backstory and personality, identify any pre-existing relationships with known NPCs.

BACKSTORY:
{backstory}

PERSONALITY:
{personality}

REPORTED RELATIONSHIPS:
{seed}

KNOWN NPC IDS: {npc_ids}

Return ONLY a JSON object with no explanation or markdown:
{{
    "relationships": {{
        "npc_id": {{
            "type": ["relationship type tags"],
            "trust": 0-100,
            "respect": 0-100,
            "affection": 0-100
            "tension": 0-100,
            "emotional_tone": "short phrase describing dynamic",
            "background": "1-3 sentences describing the pre-play history",
            "shared_history": ["any specific events mentioned in the backstory"],
            "unresolved_threads": ["any unresolved elements from the backstory"]
        }}
    }}
}}

Only include NPCs explicitly mentioned or strongly implied in the backstory.

VALID RELATIONSHIP TYPES: {Config.RELATIONSHIP_TYPES}

Only use types from the above list for the "type" field.

If no relationships are present, return {{"relationships": {{}}}}
"""

    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=5000
    )

    try:
        content = response.choices[0].message.content.strip()
        print(f"DEBUG seed_relationships raw response: {content}")
        data = parse_llm_json(content)
        seeded = data.get("relationships", {})

        for npc_id, rel in seeded.items():
            if npc_id in state["world_state"]["relationships"]:
                state["world_state"]["relationships"][npc_id].update(rel)
            else:
                state["world_state"]["relationships"][npc_id] = rel

    # Mark as met since they exist in the player's history
            if npc_id not in state["world_state"]["known_npcs"]:
                state["world_state"]["known_npcs"].append(npc_id)

    except json.JSONDecodeError:
        print("Warning: relationship seeding returned malformed JSON")

# ========================================
# UPDATE RELATIONSHIPS
# ========================================

def update_relationship_types(existing_types, new_types):
    updated = set(existing_types)
    for new_type in new_types:
        to_remove = set(Config.RELATIONSHIP_TYPE_SUPERSEDES.get(new_type, []))
        updated = updated - to_remove
        updated.add(new_type)
    return list(updated)

def apply_relationship_updates(state, updates):

    valid_types = set(Config.RELATIONSHIP_TYPES)
    relationships = state["world_state"].get("relationships", {})

    for npc_id, update in updates.items():
        if npc_id not in relationships:
            relationships[npc_id] = default_relationship_entry()

        rel = relationships[npc_id]

        if npc_id not in state["world_state"]["known_npcs"]:
            state["world_state"]["known_npcs"].append(npc_id)

        if update.get("type"):
            validated_types = [t for t in update["type"] if t in valid_types]
            if validated_types:
                rel["type"] = update_relationship_types(rel.get("type", ["unknown"]), validated_types)

        rel["trust"] = max(0, min(100, rel.get("trust", 50) + update.get("trust_delta", 0)))
        rel["respect"] = max(0, min(100, rel.get("respect", 50) + update.get("respect_delta", 0)))
        rel["affection"] = max(0, min(100, rel.get("affection", 30) + update.get("affection_delta", 0)))
        rel["tension"] = max(0, min(100, rel.get("tension", 20) + update.get("tension_delta", 0)))

        if update.get("emotional_tone"):
            rel["emotional_tone"] = update["emotional_tone"]

        if update.get("new_history"):
            rel["shared_history"].append(update["new_history"])

        resolved = update.get("resolved_threads", [])
        rel["unresolved_threads"] = [
            t for t in rel.get("unresolved_threads", [])
            if t not in resolved
        ]

        for thread in update.get("new_threads", []):
            if thread not in rel["unresolved_threads"]:
                rel["unresolved_threads"].append(thread)

    state["world_state"]["relationships"] = relationships

# ========================================
# RELATIONSHIP SUMMARIZATION
# ========================================

async def summarize_and_update_relationships(state):

    logs_to_summarize = state["logs"]["chat_log"][-5:]
    if not logs_to_summarize:
        return

    log_text = ""
    for entry in logs_to_summarize:
        log_text += f"Player: {entry['player']}\n"
        log_text += f"Narration: {entry['narration']}\n"
        if entry.get("npcs_present"):
            log_text += f"NPCs Present: {entry['npcs_present']}\n"

    relationships = state["world_state"].get("relationships", {})
    active_npc_ids = list(set(
        npc
        for entry in logs_to_summarize
        for npc in entry.get("npcs_present", [])
    ))

    current_relationships = {
        npc_id: relationships[npc_id]
        for npc_id in active_npc_ids
        if npc_id in relationships
    }

    prompt = f"""
You are analyzing a chunk of roleplay logs from a Jujutsu Kaisen narrative RPG.

LOGS:
{log_text}

CURRENT RELATIONSHIP DATA FOR ACTIVE NPCS:
{json.dumps(current_relationships, indent=2)}

VALID RELATIONSHIP TYPES: {Config.RELATIONSHIP_TYPES}

Return ONLY a JSON object with no explanation or markdown:
{{
    "summary": {{
        "location": "primary location",
        "narrative_summary": "2-3 sentence summary of events",
        "decisions": ["significant player character decisions"],
        "npc_interactions": {{
            "npc_id": "1-2 sentence summary of interaction"
        }},
        "emotional_beats": ["significant emotional moments"],
        "unresolved_threads": ["anything left unresolved"]
    }},
    "relationship_updates": {{
        "npc_id": {{
            "type": ["updated relationship types"],
            "trust_delta": 0,
            "respect_delta": 0,
            "affection_delta": 0,
            "tension_delta": 0,
            "emotional_tone": "updated tone",
            "new_history": "one sentence describing what happened worth logging",
            "resolved_threads": ["any threads now resolved"],
            "new_threads": ["any new unresolved threads"]
        }}
    }}
}}

Rules:
- Only include NPCs who actually appeared in the logs in relationship_updates
- trust_delta, respect_delta, affection_delta, tension_delta should be integers between -20 and +20
- Only log relationship_updates if something meaningfully changed
- resolved_threads should contain exact strings from the existing unresolved_threads list
"""

    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4500
    )

    try:
        content = response.choices[0].message.content.strip()
        data = parse_llm_json(content)

        summary = data.get("summary", {})
        state["logs"]["summaries"].append(summary)

        updates = data.get("relationship_updates", {})
        apply_relationship_updates(state, updates)

    except json.JSONDecodeError:
        print("Warning: summarizer returned malformed JSON")