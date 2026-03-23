from config import Config
from openai import AsyncOpenAI
from prompt import build_messages
from data import load_all_lore
from scene_tracker import detect_scene, update_scene
from relationships import summarize_and_update_relationships
from state import save_state

client = AsyncOpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.BASE_URL
)

async def generate_narration(state, player_input):
    messages = build_messages(state, player_input)

    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=messages,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )

    return response.choices[0].message.content

async def process_turn(state, player_input):
    lore = load_all_lore()
    narration = await generate_narration(state, player_input)
    result = await detect_scene(state, narration, lore)
    if result:
        update_scene(state, result)
    state["logs"]["chat_log"].append({
        "player": player_input,
        "narration": narration,
        "npcs_present": state["world_state"]["active_npcs"].copy()
    })
    if len(state["logs"]["chat_log"]) % 5 == 0:
        await summarize_and_update_relationships(state)
    save_state(state)
    return narration
