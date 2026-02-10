# Deploy ขึ้น Render.com (Docker) – รวมที่เดียว

คู่มือ deploy StoryTale ขึ้น [Render.com](https://render.com) แบบ **รวมที่เดียว**: หน้าเว็บ (React) + API (FastAPI) ใน Web Service เดียว ใช้ Docker

เปิด **https://your-service.onrender.com** จะได้หน้าเว็บเต็ม พร้อม API ที่ `/api/*`

---

## 1. สิ่งที่ต้องมีใน Repo

- **Dockerfile ที่ root** – build หน้าเว็บ (Vite/React) แล้ว copy ไปใน image, รัน backend (FastAPI) และ serve ไฟล์ static + SPA
- **`.dockerignore` ที่ root** – ไม่ส่ง `mobile`, `.git` ฯลฯ (โฟลเดอร์ `web` ต้องมีใน build)

---

## 2. สร้าง Web Service บน Render

1. เข้า [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**
2. เชื่อม GitHub repo (เช่น `Yorism7/STORYTALE`)
3. ตั้งค่า:
   - **Name:** ชื่อ service (เช่น STORYTALE)
   - **Region:** เลือกที่ใกล้ผู้ใช้
   - **Runtime:** **Docker**
   - **Root Directory:** ว่างไว้ (ใช้ root ของ repo)
4. กด **Create Web Service**

Render จะโหลด repo แล้วรัน `docker build` จาก root จึงต้องมี **Dockerfile ที่ root**

---

## 3. Environment Variables (ถ้าต้องใช้)

ไปที่ tab **Environment** ของ service แล้วเพิ่มตามที่ backend ใช้ เช่น:

| Key | ความหมาย | ตัวอย่าง |
|-----|-----------|----------|
| `STORYTELL_DB_DIR` | โฟลเดอร์เก็บ SQLite (ใน container) | `/data` (default ใน Dockerfile) |
| `POLLINATIONS_API_KEY` | API key สำหรับ Pollinations (ถ้าใช้) | (ค่าจาก Pollinations) |
| `PORT` | Render ส่งมาให้อัตโนมัติ ไม่ต้องตั้ง | - |

---

## 4. Free Tier ของ Render

- **ฟรี** แต่มีข้อจำกัด:
  - Instance จะ **spin down หลังไม่มี traffic ~15 นาที**
  - Request แรกหลัง spin down อาจช้า **~50 วินาที** (cold start)
- **Deploy:** ได้เรื่อยๆ ตามแผนฟรี
- **Persistent Disk:** **ใช้กับ Free tier ไม่ได้** (ดูหัวข้อถัดไป)

---

## 5. เรื่อง Database (DB) — สำคัญ

Backend ใช้ **SQLite** เก็บที่ `STORYTELL_DB_DIR` (ใน Docker = `/data`)

### บน Render Free tier: **ข้อมูล DB หายได้**

- ไฟล์ระบบของ container เป็น **ephemeral** (ชั่วคราว)
- ทุกครั้งที่:
  - **Redeploy**
  - **Restart**
  - **Spin down** (หลังไม่มี traffic แล้ว Render ปิด instance)
- container ถูกสร้างใหม่ → ไฟล์ใน container **หายหมด** รวมถึงไฟล์ SQLite ที่ `/data`

**สรุป:** ข้อมูลเรื่องที่สร้างไว้ **ไม่ถาวร** บน Free tier ถ้าใช้แค่ SQLite ใน container

### ทางเลือกถ้าอยากให้ข้อมูลไม่หาย

| ทางเลือก | ข้อมูล DB | หมายเหตุ |
|----------|-----------|----------|
| **ใช้ Free + SQLite อย่างเดียว** | **หาย** เมื่อ redeploy / spin down | เหมาะแค่ demo / ทดลอง |
| **Render Persistent Disk** | ไม่หาย | ต้อง **อัปเกรดเป็น paid** แล้วแนบ disk ที่ path เช่น `/data` |
| **PostgreSQL ภายนอก** | ไม่หาย | ใช้ Render Free PostgreSQL หรือ Neon / Supabase (ฟรี) แล้วแก้ backend ให้ต่อ Postgres แทน SQLite |

เอกสาร Render: [Persistent Disks](https://render.com/docs/disks), [Deploy for Free](https://render.com/docs/free)

---

## 6. สรุป Checklist

- [ ] Repo มี **Dockerfile** ที่ root (build จาก `backend/`)
- [ ] Repo มี **`.dockerignore`** ที่ root
- [ ] Push ขึ้น GitHub แล้วให้ Render deploy
- [ ] ตั้ง Environment variables ที่ tab **Environment** (ถ้ามี)
- [ ] เข้าใจว่า Free tier: **DB (SQLite) หายเมื่อ redeploy/spin down** ถ้าอยากเก็บข้อมูลถาวรต้องใช้ Persistent Disk (paid) หรือ PostgreSQL

---

## 7. ลิงก์อ้างอิง

- [Render – Deploy for Free](https://render.com/docs/free)
- [Render – Persistent Disks](https://render.com/docs/disks)
- [Render – Docker](https://render.com/docs/docker)
