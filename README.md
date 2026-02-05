# StoryTale

**StoryTale** – AI-powered children’s stories: generate a story from a topic, with illustrations, read-aloud audio (Edge TTS), and video export.

**StoryTale** – แอปนิทานเด็กจาก AI: สร้างเรื่องจากหัวข้อ พร้อมภาพประกอบ เสียงอ่าน (Edge TTS) และส่งออกวิดีโอ

---

## Run with Docker (recommended)

```bash
# From project root
docker compose up --build
```

- Open **http://localhost** (port 80). Do not use `:8000` — the web server proxies `/api` to the backend.
- SQLite data is stored in the `storytell_data` volume.
- **API key:** Create `backend/.env` and set `POLLINATIONS_API_KEY=...` (get a key at [enter.pollinations.ai](https://enter.pollinations.ai)).

Stop: `docker compose down`

### Docker summary

| Item        | Description |
|------------|-------------|
| **Web**    | Nginx on port 80, serves frontend and proxies `/api` to backend |
| **Backend**| FastAPI on port 8000 (internal), no direct host exposure |
| **Volume** | `storytell_data` for SQLite `stories.db` |
| **Env**    | `backend/.env` for `POLLINATIONS_API_KEY`, `STORYTELL_DB_DIR=/data` in container |

---

## Run without Docker

### Backend

```bash
cd backend
pip install -r requirements.txt
# Optional: create .env with POLLINATIONS_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Web

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173 (Vite proxies API to backend :8000).

### Mobile (Kivy)

```bash
cd mobile
pip install -r requirements.txt
# Windows
set STORYTELL_API_BASE=http://<YOUR_PC_IP>:8000
# macOS/Linux
export STORYTELL_API_BASE=http://<YOUR_PC_IP>:8000
python main.py
```

---

## Project structure

- **backend/** – FastAPI, Pollinations (text + image), SQLite, Edge TTS, video export (MoviePy)
- **web/** – Vite + React + TypeScript + Tailwind (form, story view, list, TTS play, video export, share link, image style/model)
- **mobile/** – Kivy (iOS/Android): form, story view, list, TTS play

---

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/story/generate` | Generate story (topic, num_episodes, image_model?, image_style?) |
| GET | `/api/story/{id}` | Get story by id |
| GET | `/api/stories` | List stories |
| GET | `/api/story/{id}/episode/{index}/audio` | TTS audio for one episode |
| POST | `/api/story/export-video` | Export story as MP4 (body: `{ "storyId": "..." }`) |

---

## ภาษาไทย (Thai)

- **รันด้วย Docker:** `docker compose up --build` แล้วเปิด http://localhost
- **Backend:** ใส่ `POLLINATIONS_API_KEY` ใน `backend/.env`
- **เว็บ:** พอร์ต 80 ผ่าน Docker; หรือ `npm run dev` ที่โฟลเดอร์ `web` (พอร์ต 5173)
- **มือถือ (Kivy):** ตั้ง `STORYTELL_API_BASE` ให้ชี้ไปที่ IP เครื่องที่รัน backend
