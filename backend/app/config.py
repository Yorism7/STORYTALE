"""App config from env."""
import os

def _get_key(name: str, default: str = "") -> str:
    v = os.environ.get(name, default) or ""
    return v.strip()

POLLINATIONS_API_KEY = _get_key("POLLINATIONS_API_KEY")
POLLINATIONS_BASE = os.environ.get("POLLINATIONS_BASE", "https://gen.pollinations.ai").strip()
