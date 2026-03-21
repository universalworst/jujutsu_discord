from config import Config
from openai import AsyncOpenAI
from prompt import build_messages

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