FROM python:3.13-slim

# System packages: build-essential/gcc for Cython (IndicTransToolkit),
# libpq-dev for psycopg, ffmpeg/libsndfile for audio, libgl for opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt

# Copy backend/ and ai/ as SIBLING folders under /app, matching what
# backend/app/main.py expects on sys.path (backend/ and its parent).
COPY backend/ ./backend/
COPY ai/ ./ai/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]