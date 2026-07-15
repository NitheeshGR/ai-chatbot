# Loads environment variables and provides app configuration (DB URL, API keys)
import os
from dotenv import load_dotenv

# Read .env file and load variables into environment
load_dotenv()

# PostgreSQL connection string — must be set in .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Hugging Face API token — must be set in .env
HF_TOKEN = os.getenv("HF_TOKEN", "")
