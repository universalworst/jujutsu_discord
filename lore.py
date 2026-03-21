import json
from data import load_all_lore
from utils import as_list

def build_lore_block(state):
    lore = load_all_lore()
    lore_block = []

    # ==============================
    # NPC_BLOCK
    # ==============================

    npc_profiles = lore.get("npc_profiles")
    locations = lore.get("locations")
    active_npcs = state["world_state"]["active_npcs"]
    known_npcs = state["world_state"]["known_npcs"]
    current_location = state["world_state"]["current_location"]
    known_locations = state["world_state"]["known_locations"]
    active_npc_block = ""
    known_npc_block = ""
    if active_npcs:
        profiles = ["== PRESENT NPCS =="]
        for npc_id in active_npcs:
            if npc_id not in known_npcs:
                known_npcs.append(npc_id)
            profile = npc_profiles.get(npc_id)
            if profile:
                profiles.append(json.dumps(profile, indent=2))
        active_npc_block = "\n".join(profiles)
    if known_npcs and not active_npcs:
        known = []
        for npc_id in known_npcs:
            npc = npc_profiles.get(npc_id)
            if npc:
                known.append(f"""
NPC: {npc['display_name']} (known)
Role: {as_list(npc['role'])} | Grade: {npc['grade']} | Affiliation: {as_list(npc['affiliation'])}
Technique: {as_list(npc['technique'])}
---""")
        known_npc_block = "\n".join(known)
    npc_block = "\n".join([active_npc_block, known_npc_block])
    lore_block.append(npc_block)

    # ==============================
    # LOCATIONS_BLOCK
    # ==============================
    locs = []
    loc = locations.get(current_location)
    if loc:
        locs.append("==CURRENT LOCATION==")
        locs.append(json.dumps(loc, indent=2))
        if current_location not in known_locations:
            known_locations.append(current_location)
    for location_id in known_locations:
        if location_id == current_location:
            continue
        known_loc = locations.get(location_id)
        if known_loc:
            locs.append("===PREVIOUSLY VISITED LOCATIONS==="
                f"  {location_id.replace('_', ' ').title()} — "
                f"{known_loc['location_type']} | "
                f"Curse Density: {known_loc['curse_density']}"
            )
    location_block = "\n".join(locs)
    lore_block.append(location_block)

    return "\n".join(lore_block)