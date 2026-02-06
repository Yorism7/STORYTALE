"""API request/response schemas - shared contract with Web and Kivy."""
from typing import Literal

from pydantic import BaseModel, Field

IMAGE_MODEL_CHOICES = Literal["flux", "zimage"]
STORY_LANG_CHOICES = Literal["en", "th"]


class GenerateStoryRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="หัวข้อหรือแนวเรื่อง")
    num_episodes: int = Field(default=5, ge=1, le=10, description="จำนวนตอน (1-10)")
    story_lang: STORY_LANG_CHOICES = Field(default="en", description="ภาษาของเรื่อง: en (English) หรือ th (ไทย)")
    image_model: IMAGE_MODEL_CHOICES = Field(default="flux", description="โมเดลภาพ: flux หรือ zimage")
    image_style: str | None = Field(default=None, max_length=100, description="สไตล์ภาพ (ไม่บังคับ)")


class EpisodeOut(BaseModel):
    text: str
    imageUrl: str


class GenerateStoryResponse(BaseModel):
    storyId: str
    title: str
    episodes: list[EpisodeOut]


class StoryListItem(BaseModel):
    storyId: str
    topic: str
    title: str
    num_episodes: int
    created_at: str
    first_episode_image_url: str | None = None


class GetStoryResponse(BaseModel):
    storyId: str
    topic: str
    title: str
    num_episodes: int
    created_at: str
    episodes: list[EpisodeOut]


class ExportVideoRequest(BaseModel):
    storyId: str
