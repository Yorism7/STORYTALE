"""Export story to MP4: image per episode + Edge TTS audio, concatenate with moviepy."""
import base64
import io
import tempfile
from pathlib import Path

from app.services.tts import text_to_audio


def _ep_text(ep) -> str:
    """ดึงข้อความจาก episode (รองรับทั้ง dict และ Pydantic EpisodeOut)."""
    return ep.get("text", "") if isinstance(ep, dict) else getattr(ep, "text", "") or ""


def _ep_image_url(ep) -> str:
    """ดึง imageUrl จาก episode (รองรับทั้ง dict และ Pydantic EpisodeOut)."""
    return ep.get("imageUrl", "") if isinstance(ep, dict) else getattr(ep, "imageUrl", "") or ""

# Lazy import moviepy (v2: ไม่มี moviepy.editor แล้ว, import จาก moviepy โดยตรง)
def _moviepy():
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip
    return ImageClip, AudioFileClip, concatenate_videoclips, ColorClip


def _data_url_to_image_path(data_url: str, dir_path: Path, index: int) -> Path:
    """Decode data URL to JPEG file; return path."""
    if not data_url.startswith("data:image"):
        raise ValueError("Not a data URL")
    payload = data_url.split(",", 1)[1]
    raw = base64.b64decode(payload)
    path = dir_path / f"ep{index}.jpg"
    path.write_bytes(raw)
    return path


async def export_story_to_mp4(story: dict) -> bytes:
    """
    story: dict with episodes: [{ text, imageUrl }].
    Returns MP4 file bytes.
    """
    ImageClip, AudioFileClip, concatenate_videoclips, ColorClip = _moviepy()
    episodes = story.get("episodes", [])
    if not episodes:
        raise ValueError("No episodes")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        clips = []
        for i, ep in enumerate(episodes):
            text = _ep_text(ep)
            image_url = _ep_image_url(ep)
            if not text:
                continue
            audio_bytes = await text_to_audio(text)
            audio_path = root / f"ep{i}.mp3"
            audio_path.write_bytes(audio_bytes)
            audio_clip = AudioFileClip(str(audio_path))
            duration = audio_clip.duration
            if image_url:
                try:
                    img_path = _data_url_to_image_path(image_url, root, i)
                    img_clip = ImageClip(str(img_path)).with_duration(duration).with_audio(audio_clip)
                except Exception:
                    img_clip = ColorClip(size=(1024, 1024), color=(255, 255, 255), duration=duration).with_audio(audio_clip)
            else:
                img_clip = ColorClip(size=(1024, 1024), color=(255, 255, 255), duration=duration).with_audio(audio_clip)
            clips.append(img_clip)
            # อย่า close audio_clip ที่นี่ — img_clip ยังอ้างถึงอยู่ ตอน write_videofile จะได้ reader เป็น None

        if not clips:
            raise ValueError("No valid clips")
        final = concatenate_videoclips(clips)
        out_path = root / "story.mp4"
        try:
            final.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
            return out_path.read_bytes()
        finally:
            final.close()
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass
    return b""
