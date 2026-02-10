# สำหรับ Render.com (และ Docker จาก root ของ repo)
# Build backend API เท่านั้น
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

ENV STORYTELL_DB_DIR=/data
VOLUME /data

EXPOSE 8000
# Render ส่ง PORT ผ่าน env ได้
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
