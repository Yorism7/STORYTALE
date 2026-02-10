"""StoryTale FastAPI app."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from app.db import init_db, StoryRepository
from app.models import (
    GenerateStoryRequest,
    GenerateStoryResponse,
    StoryListItem,
    GetStoryResponse,
    ExportVideoRequest,
)
from app.services import StoryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="StoryTale API",
    description="AI-generated children's storybook: text + images + TTS + video",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = StoryRepository()
story_service = StoryService(repo)

# โฟลเดอร์ static (เว็บที่ build แล้ว) – ใน Docker อยู่ที่ /app/static
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/")
def root():
    """Root: serve หน้าเว็บ (index.html) ถ้ามี build แล้ว ไม่ก็คืน API info."""
    index_html = STATIC_DIR / "index.html"
    if index_html.is_file():
        return FileResponse(index_html, media_type="text/html")
    return {
        "app": "StoryTale API",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/story/generate, /api/stories, /api/story/{id}, ...",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """ไม่มี favicon → 204 No Content เพื่อไม่ให้เบราว์เซอร์ log 404."""
    return Response(status_code=204)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/story/generate", response_model=GenerateStoryResponse)
async def generate_story(body: GenerateStoryRequest):
    """Generate story via Pollinations, save to SQLite, return storyId + episodes."""
    return await story_service.generate(
        body.topic, body.num_episodes, body.story_lang, body.image_model, body.image_style
    )


@app.get("/api/story/{story_id}", response_model=GetStoryResponse)
async def get_story(story_id: str):
    """Load story by id from SQLite."""
    story = await asyncio.to_thread(repo.get_story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@app.get("/api/stories", response_model=list[StoryListItem])
async def list_stories(limit: int = 20, offset: int = 0):
    """List stories (newest first)."""
    return await asyncio.to_thread(repo.list_stories, limit, offset)


@app.get("/api/story/{story_id}/episode/{index}/audio")
async def get_episode_audio(story_id: str, index: int):
    """Generate TTS audio for one episode (Edge TTS), return MP3."""
    story = await asyncio.to_thread(repo.get_story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    episodes = story.get("episodes", [])
    if index < 0 or index >= len(episodes):
        raise HTTPException(status_code=404, detail="Episode not found")
    ep = episodes[index]
    text = ep.get("text", "") if isinstance(ep, dict) else getattr(ep, "text", "") or ""
    if not text:
        raise HTTPException(status_code=400, detail="Episode has no text")
    from app.services.tts import text_to_audio
    audio_bytes = await text_to_audio(text)
    return Response(content=audio_bytes, media_type="audio/mpeg")


@app.post("/api/story/export-video")
async def export_video(body: ExportVideoRequest):
    """Generate MP4 from story: Edge TTS per episode + images, concatenate with moviepy."""
    story = await asyncio.to_thread(repo.get_story, body.storyId)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    try:
        from app.services.video_export import export_story_to_mp4
        mp4_bytes = await export_story_to_mp4(story)
    except Exception as e:
        import traceback
        print(f"[StoryTale] export-video error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Export failed")
    return Response(content=mp4_bytes, media_type="video/mp4")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    """Serve ไฟล์ static หรือ index.html สำหรับ SPA (รวม deploy ที่เดียว)."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    if not STATIC_DIR.is_dir():
        raise HTTPException(status_code=404, detail="Not found")
    file_path = (STATIC_DIR / full_path).resolve()
    try:
        if not file_path.is_relative_to(STATIC_DIR.resolve()):
            raise HTTPException(status_code=404, detail="Not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")
    if file_path.is_file():
        return FileResponse(file_path)
    index_html = STATIC_DIR / "index.html"
    if index_html.is_file():
        return FileResponse(index_html, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")
