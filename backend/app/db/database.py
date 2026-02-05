"""SQLite setup and schema (sync sqlite3, use from async via to_thread)."""
import os
import sqlite3
from pathlib import Path

DB_DIR = Path(os.environ.get("STORYTELL_DB_DIR", "./data"))
DB_PATH = DB_DIR / "stories.db"


def get_db_path() -> Path:
    return DB_PATH


def init_db_sync() -> None:
    """Create data dir and tables if not exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            title TEXT NOT NULL,
            num_episodes INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id TEXT NOT NULL,
            ordinal INTEGER NOT NULL,
            text TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_prompt TEXT,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    """)
    conn.commit()
    conn.close()
    print(f"[StoryTale] SQLite initialized at {DB_PATH}")
