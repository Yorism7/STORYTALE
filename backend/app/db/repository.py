"""Story repository - save/load/list from SQLite (sync, wrap in to_thread when needed)."""
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.db.database import get_db_path
from app.models import EpisodeOut


def _row_factory(cursor, row):
    return dict(zip([c[0] for c in cursor.description], row))


class StoryRepository:
    def __init__(self, db_path: Optional[str] = None):
        self._path = db_path or str(get_db_path())

    def save_story(
        self,
        story_id: str,
        topic: str,
        title: str,
        num_episodes: int,
        episodes: list[tuple[str, str, Optional[str]]],
    ) -> None:
        """episodes: list of (text, image_url, image_prompt)."""
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self._path)
        conn.execute(
            "INSERT INTO stories (id, topic, title, num_episodes, created_at) VALUES (?, ?, ?, ?, ?)",
            (story_id, topic, title, num_episodes, now),
        )
        for i, (text, image_url, image_prompt) in enumerate(episodes):
            conn.execute(
                "INSERT INTO episodes (story_id, ordinal, text, image_url, image_prompt) VALUES (?, ?, ?, ?, ?)",
                (story_id, i, text, image_url, image_prompt or ""),
            )
        conn.commit()
        conn.close()
        print(f"[StoryTale] Saved story {story_id} with {len(episodes)} episodes")

    def get_story(self, story_id: str) -> Optional[dict]:
        """Return { title, topic, num_episodes, created_at, episodes: [EpisodeOut] } or None."""
        conn = sqlite3.connect(self._path)
        conn.row_factory = _row_factory
        cur = conn.execute(
            "SELECT id, topic, title, num_episodes, created_at FROM stories WHERE id = ?",
            (story_id,),
        )
        story_row = cur.fetchone()
        if not story_row:
            conn.close()
            return None
        cur = conn.execute(
            "SELECT ordinal, text, image_url FROM episodes WHERE story_id = ? ORDER BY ordinal",
            (story_id,),
        )
        rows = cur.fetchall()
        conn.close()
        episodes = [
            EpisodeOut(text=r["text"], imageUrl=r["image_url"])
            for r in rows
        ]
        return {
            "storyId": story_row["id"],
            "topic": story_row["topic"],
            "title": story_row["title"],
            "num_episodes": story_row["num_episodes"],
            "created_at": story_row["created_at"],
            "episodes": episodes,
        }

    def list_stories(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Return list of { storyId, topic, title, num_episodes, created_at, first_episode_image_url }."""
        conn = sqlite3.connect(self._path)
        conn.row_factory = _row_factory
        cur = conn.execute(
            """SELECT s.id, s.topic, s.title, s.num_episodes, s.created_at,
                      (SELECT e.image_url FROM episodes e WHERE e.story_id = s.id ORDER BY e.ordinal LIMIT 1) AS first_episode_image_url
               FROM stories s ORDER BY s.created_at DESC LIMIT ? OFFSET ?""",
            (limit, offset),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "storyId": r["id"],
                "topic": r["topic"],
                "title": r["title"],
                "num_episodes": r["num_episodes"],
                "created_at": r["created_at"],
                "first_episode_image_url": r.get("first_episode_image_url") or None,
            }
            for r in rows
        ]

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())
