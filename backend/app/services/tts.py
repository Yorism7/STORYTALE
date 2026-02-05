"""Edge TTS – generate audio from text."""
import pathlib
import tempfile
import edge_tts

# Thai voice; fallback to English if needed
DEFAULT_VOICE = "th-TH-PremwadeeNeural"


async def text_to_audio(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Return MP3 bytes for the given text. edge_tts.save() รับ path เท่านั้น ไม่รับ BytesIO."""
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    try:
        await communicate.save(path)
        return pathlib.Path(path).read_bytes()
    finally:
        pathlib.Path(path).unlink(missing_ok=True)
