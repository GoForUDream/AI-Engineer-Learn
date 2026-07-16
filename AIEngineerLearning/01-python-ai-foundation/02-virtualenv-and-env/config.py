import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: 'GEMINI_API_KEY' is missing from the environment variables.\n"
        "Please check your .env file and ensure it is properly configured."
    )

APP_ENV = os.getenv("APP_ENV", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
