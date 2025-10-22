import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    @property
    def OPENAI_API_KEY(self):
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not found in environment or .env file.")
        return key

settings = Settings()
