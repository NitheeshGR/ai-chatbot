import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_chatbot"
)
HF_TOKEN = os.getenv("HF_TOKEN", "")
