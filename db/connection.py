import os
import json
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def load_dbconfig(file_path: str = "config/db.json") -> dict:
    """Load database configuration from JSON (for local development)."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)["database"]
    except FileNotFoundError:
        return {}

@contextmanager
def get_connection():
    """
    Context manager for PostgreSQL connection.
    Prioritises DATABASE_URL (for NeonDB or EC2),
    falls back to local db.json if not found.
    """
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        conn = psycopg2.connect(db_url)
    else:
        config = load_dbconfig()
        conn = psycopg2.connect(
            database=config.get("name"),
            user=config.get("user"),
            password=config.get("password"),
            host=config.get("host"),
            port=config.get("port"),
        )

    try:
        yield conn
    finally:
        conn.close()
