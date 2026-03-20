# ========================================
# IMPORTS
# ========================================

import json

# ========================================
# LLM PARSING
# ========================================

def parse_llm_json(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    return json.loads(content)

def as_list(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value) if value else ""