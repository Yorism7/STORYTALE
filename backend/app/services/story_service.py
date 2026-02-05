"""Story generation: Pollinations -> images -> SQLite."""
import asyncio
import base64
from typing import Optional

from app.db import StoryRepository
from app.models import GenerateStoryResponse, EpisodeOut
from app.services.pollinations import generate_story_json, generate_image


class StoryService:
    def __init__(self, repo: Optional[StoryRepository] = None):
        self.repo = repo or StoryRepository()

    async def generate(
        self,
        topic: str,
        num_episodes: int,
        story_lang: str = "en",
        image_model: str = "flux",
        image_style: str | None = None,
    ) -> GenerateStoryResponse:
        """Generate story JSON, then image per episode, save to DB, return response."""
        lang = story_lang if story_lang in ("en", "th") else "en"
        story_data = await generate_story_json(topic, num_episodes, story_lang=lang)
        title = story_data["title"]
        episodes_data = story_data["episodes"][:num_episodes]
        model = image_model if image_model in ("flux", "zimage") else "flux"
        character_description = (story_data.get("characterDescription") or "").strip()
        art_style = (story_data.get("artStyle") or "").strip()
        if character_description or art_style:
            print(f"[StoryTale] Image model: {model}, consistent: characters={bool(character_description)}, artStyle={bool(art_style)}")
        else:
            print(f"[StoryTale] Image model: {model}")

        episodes_out: list[EpisodeOut] = []
        episodes_for_db: list[tuple[str, str, Optional[str]]] = []

        for i, ep in enumerate(episodes_data):
            text = ep.get("text", "")
            image_prompt = ep.get("imagePrompt", "children's book illustration")
            try:
                img_bytes = await generate_image(
                    image_prompt,
                    style_suffix=image_style,
                    model=model,
                    character_description=character_description or None,
                    art_style=art_style or None,
                )
                # Return as data URL so frontend can display without extra storage
                b64 = base64.b64encode(img_bytes).decode("ascii")
                image_url = f"data:image/jpeg;base64,{b64}"
            except Exception as e:
                print(f"[StoryTale] Image gen failed for episode {i}: {e}")
                image_url = ""
            episodes_out.append(EpisodeOut(text=text, imageUrl=image_url))
            episodes_for_db.append((text, image_url, image_prompt))

        story_id = StoryRepository.new_id()
        await asyncio.to_thread(
            self.repo.save_story,
            story_id=story_id,
            topic=topic,
            title=title,
            num_episodes=len(episodes_out),
            episodes=episodes_for_db,
        )
        return GenerateStoryResponse(storyId=story_id, title=title, episodes=episodes_out)
