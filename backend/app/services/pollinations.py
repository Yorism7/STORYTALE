"""Pollinations API client: chat completions (story JSON) + image generation."""
import json
import random
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

CRITICAL – Consistent look in every illustration (same characters + same art style):
- Add "characterDescription": one short English phrase for the main characters' appearance so they look THE SAME in every picture (e.g. "a small brown rabbit with white belly and pink ears, a green turtle with round shell and friendly smile").
- Add "artStyle": one short English phrase for the VISUAL STYLE of all illustrations, so every image looks like the same book. Be specific: technique, colors, mood (e.g. "soft watercolor painting, pastel colors, rounded shapes, warm lighting, gentle shadows" or "flat cartoon style, bright colors, clean lines, friendly and cheerful"). This will be applied to every episode image.
- Each episode "imagePrompt" = only the SCENE or action for that moment (where they are, what they do). Do NOT repeat character looks or art style in each imagePrompt.

Rules:
- {lang_rule}
- Each episode: "text" = 2–4 short sentences, simple words, positive message.
- Each episode: "imagePrompt" = one English phrase for the scene/situation only, e.g. "in a sunny forest by a stream", "at the finish line cheering".
- No violence, no fear; gentle and safe for kids.

Output ONLY valid JSON, no markdown or extra text:
{{"title": "Story title", "characterDescription": "short visual description of main characters", "artStyle": "short description of illustration style for the whole story", "episodes": [{{"text": "...", "imagePrompt": "..."}}, ...]}}"""

    seed = random.randint(1, 999_999)
    variation_hints = [
        "Create a unique, surprising version—avoid the most obvious plot.",
        "Tell a fresh take on this theme; surprise the reader with an unexpected twist or setting.",
        "Invent a different angle or character focus so this story feels new.",
        "Use an unusual setting or situation for this topic.",
        "Make the moral or journey different from the typical story for this theme.",
    ]
    hint = random.choice(variation_hints)
    user = f"Write a children's story about: {topic}. Use exactly {num_episodes} episodes. [Variation seed: {seed}] {hint}"

    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": random.uniform(0.75, 0.92),
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
    if "characterDescription" not in parsed or not str(parsed.get("characterDescription", "")).strip():
        parsed["characterDescription"] = ""
    if "artStyle" not in parsed or not str(parsed.get("artStyle", "")).strip():
        parsed["artStyle"] = ""
    print(f"[StoryTale] Generated story title: {parsed.get('title')}, episodes: {len(parsed.get('episodes', []))}, characterDescription: {'yes' if parsed.get('characterDescription') else 'no'}, artStyle: {'yes' if parsed.get('artStyle') else 'no'}")
    return parsed


async def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    style_suffix: str | None = None,
    model: str = IMAGE_MODEL_DEFAULT,
    character_description: str | None = None,
    art_style: str | None = None,
) -> bytes:
    """Generate one image from prompt; returns image bytes (JPEG). model: flux | zimage.
    character_description: ตัวละครคงที่ทุกภาพ | art_style: แนวภาพจาก LLM (ใช้เมื่อไม่มี style_suffix).
    style_suffix: สไตล์ที่ผู้ใช้เลือก – ใช้เป็นแนวหลักของทุกภาพให้เหมือนกันทั้งเรื่อง"""
    # ตัวละครคงที่ทุกภาพ
    base = (character_description.strip() + ". ") if character_description and character_description.strip() else ""
    # สไตล์ภาพ: ถ้าผู้ใช้เลือกมาให้ใช้เป็นแนวหลักทั้งเรื่อง ไม่ก็ใช้ art_style จาก LLM หรือค่าเริ่มต้น
    if style_suffix and style_suffix.strip():
        style_part = (
            f"{style_suffix.strip()}, same visual style and character design in every scene, "
            "consistent throughout the story, "
        )
    else:
        style_part = (art_style.strip() + ", ") if art_style and art_style.strip() else "children's book illustration, soft colors, cartoon style, "
        style_part += "same visual style and character design in every scene, "
    safe_prompt = f"{base}{prompt}, {style_part}friendly, safe for kids, no violence, no dark themes"
    encoded = urllib.parse.quote(safe_prompt)
    url = f"{IMAGE_BASE}/{encoded}"
    params = _image_params(prompt, width, height, model=model)
    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.content
