import psycopg2
import json
import os
from contextlib import contextmanager


def load_dbconfig(file_path: str = "config/db.json") -> dict:
    """Load database configuration from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)["database"]


@contextmanager
def get_connection():
    """
    Context manager for PostgreSQL connection.
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("...")
    """
    config = load_dbconfig()
    conn = psycopg2.connect(
        database=config["name"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
    )
    try:
        yield conn
    finally:
        conn.close()
