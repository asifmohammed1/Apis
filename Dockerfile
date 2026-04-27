FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Use PORT env variable (Render/Railway/etc set this), fallback to 8000
ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT