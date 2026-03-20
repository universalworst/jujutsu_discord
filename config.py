from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    # ====================================
    # API
    # ====================================
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    TOKEN = os.getenv("TOKEN")
    BASE_URL = "https://api.deepseek.com"

    # ====================================
    # MODEL SETTINGS
    # ====================================
    MODEL_NAME = "deepseek-chat"
    TEMPERATURE = 0.8
    MAX_TOKENS = 800

    # ====================================
    # SAVE DIRECTORY SETTINGS
    # ====================================
    SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
    os.makedirs(SAVE_DIR, exist_ok=True)
