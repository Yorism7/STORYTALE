# StoryTale Backend

FastAPI + Pollinations + SQLite + Edge TTS + video export (MoviePy).

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Env

Create `backend/.env` (or set env vars):

- `POLLINATIONS_API_KEY` – optional; improves rate limits.
- `STORYTELL_DB_DIR` – optional; default `./data`, SQLite file `stories.db`.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
