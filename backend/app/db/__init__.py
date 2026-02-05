from app.db.database import init_db_sync, get_db_path

def init_db():
    """Sync init; call from lifespan (fast)."""
    init_db_sync()

from app.db.repository import StoryRepository

__all__ = ["init_db", "get_db_path", "StoryRepository"]
