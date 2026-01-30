import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DB_PATH = "data/products.db"

# LLM
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY = 2

# DB
DB_MAX_RETRIES = 3
DB_RETRY_DELAY = 1
