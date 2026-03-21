import json, os

def load_all_lore(folder="world_data"):
    lore = {}
    if not os.path.exists(folder):
        return lore
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            key = filename.replace(".json", "")
            path = os.path.join(folder, filename)
            try:
                with open(path) as f:
                    lore[key] = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {filename} is malformed, skipping.")
    return lore