# ---------- 1. Base image ----------
FROM python:3.12-slim

# ---------- 2. Environment variables ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------- 3. System dependencies ----------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---------- 4. Install Python dependencies ----------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------- 5. Copy project code ----------
COPY . .

# ---------- 6. Expose port ----------
# Render automatically sets $PORT, but exposing 8000 is fine for local testing
EXPOSE 8000

# ---------- 7. Start the app ----------
# Render sets $PORT in the environment
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
