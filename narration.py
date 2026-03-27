from config import Config
from openai import AsyncOpenAI
from prompt import build_messages, build_session_messages
from data import load_all_lore
from scene_tracker import detect_scene, update_scene, detect_scene_session, update_scene_session
from relationships import summarize_and_update_relationships, summarize_and_update_relationships_session
from state import save_state, save_session

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

# ========== SESSION NARRATION ===========

async def generate_narration_session(session, messages):
    print("Entered generate_narration_session (narration.py)")
    content = build_session_messages(session, messages)

    response = await client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=content,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )

    return response.choices[0].message.content

async def process_turn_session(session, messages):
    print("Entered process_turn_session (narration.py)")
    lore = load_all_lore()
    channel_id = session["channel_id"]
    print("Generating narration... (narration.py)")
    narration = await generate_narration_session(session, messages)
    print("Narration generated. (narration.py)")
    result = await detect_scene_session(session, narration, lore)
    print("Scene detected. (narration.py)")
    if result:
        update_scene_session(session, result)
        print("Scene updated. (narration.py)")
    try:
        for msg in messages:
            print(f"Messages to append: {messages[:50]}")
            session["session_log"].append({
                "author": msg["author"],
                "content": msg["content"],
                "npcs_present": session["active_npcs"].copy()
            })
            print("Session appended: Messages (narration.py)")
    except Exception as e:
        print(f"Exception: {e} (narration.py)")
    print(f"About to append narration: {narration[:50]}")
    session["session_log"].append({
        "narration": narration
    })
    print("Session appended: narration")
    print("Updating relationships...")
    await summarize_and_update_relationships_session(session, narration)
    print("Relationships summarized and updated (narration.py)")
    session["messages"] = []
    save_session(session, channel_id)
    print("Session saved (narration.py)")
    return narration