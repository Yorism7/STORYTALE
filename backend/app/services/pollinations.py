"""Pollinations API client: chat completions (story JSON) + image generation."""
import json
import urllib.parse
from typing import Any

import httpx

from app.config import POLLINATIONS_API_KEY, POLLINATIONS_BASE

CHAT_URL = f"{POLLINATIONS_BASE}/v1/chat/completions"
IMAGE_BASE = f"{POLLINATIONS_BASE}/image"


def _headers() -> dict:
    """Headers for chat: ไม่ส่ง Authorization เพื่อใช้ ?key= อย่างเดียว (ลดโอกาส 401)."""
    return {"Content-Type": "application/json"}


# โมเดล: บทความ = gemini-fast, ภาพ = flux หรือ zimage
CHAT_MODEL = "gemini-fast"
IMAGE_MODEL_DEFAULT = "flux"  # Flux Schnell; ทางเลือก: zimage (Z-Image Turbo)


def _image_params(prompt: str, width: int = 1024, height: int = 1024, model: str = IMAGE_MODEL_DEFAULT) -> dict:
    p = {"width": width, "height": height, "enhance": "false", "model": model}
    if POLLINATIONS_API_KEY:
        p["key"] = POLLINATIONS_API_KEY
    return p


async def generate_story_json(topic: str, num_episodes: int, story_lang: str = "en") -> dict[str, Any]:
    """Call Pollinations chat completions; return parsed JSON. story_lang: en = English, th = Thai."""
    lang_rule = (
        'Write the story title and ALL episode "text" in Thai (ภาษาไทย).'
        if story_lang == "th"
        else 'Write the story title and ALL episode "text" in English.'
    )
    system = f"""You are a children's story writer for ages 3–8. Create a short, wholesome story with exactly {num_episodes} episodes (chapters).
Rules:
- {lang_rule}
- Each episode: "text" = 2–4 short sentences, simple words, positive message.
- Each episode: "imagePrompt" = one English phrase for a single illustration: friendly characters, soft colors, children's book style (e.g. "cute rabbit and turtle in a sunny forest, watercolor illustration, soft pastel colors, no text").
- No violence, no fear; gentle and safe for kids.
Output ONLY valid JSON, no markdown or extra text:
{{"title": "Story title", "episodes": [{{"text": "...", "imagePrompt": "..."}}, ...]}}"""

    user = f"Write a children's story about: {topic}. Use exactly {num_episodes} episodes."

    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
    }
    # Pollinations: ใช้ ?key= อย่างเดียว (ถ้าส่ง Bearer ด้วยบางครั้งได้ 401)
    url = CHAT_URL
    if POLLINATIONS_API_KEY:
        url = f"{CHAT_URL}?key={urllib.parse.quote(POLLINATIONS_API_KEY)}"
        # Debug: ตรวจว่า key โหลดแล้ว (mask ไว้)
        key_preview = POLLINATIONS_API_KEY[:8] + "..." if len(POLLINATIONS_API_KEY) > 8 else "***"
        print(f"[StoryTale] Pollinations API key loaded: {key_preview}")
    else:
        print("[StoryTale] POLLINATIONS_API_KEY not set; request may be rate-limited or 401.")
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload, headers=_headers())
        r.raise_for_status()
        data = r.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    # Strip markdown code block if present
    if content.strip().startswith("```"):
        lines = content.strip().split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    parsed = json.loads(content)
    if "title" not in parsed or "episodes" not in parsed:
        raise ValueError("Invalid story JSON: missing title or episodes")
    print(f"[StoryTale] Generated story title: {parsed.get('title')}, episodes: {len(parsed.get('episodes', []))}")
    return parsed


async def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    style_suffix: str | None = None,
    model: str = IMAGE_MODEL_DEFAULT,
) -> bytes:
    """Generate one image from prompt; returns image bytes (JPEG). model: flux | zimage."""
    # Child-friendly style: soft, illustration; optional style from user
    style_extra = f", {style_suffix}" if style_suffix else ""
    safe_prompt = f"{prompt}, children's book illustration, soft colors, cartoon style{style_extra}, friendly, safe for kids, no violence, no dark themes"
    encoded = urllib.parse.quote(safe_prompt)
    url = f"{IMAGE_BASE}/{encoded}"
    params = _image_params(prompt, width, height, model=model)
    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.content
