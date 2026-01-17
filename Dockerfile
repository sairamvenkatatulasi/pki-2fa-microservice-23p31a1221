FROM python:3.10-slim

WORKDIR /app

# System deps for cryptography
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    cron \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Make pip reliable on slow networks
RUN pip install --upgrade pip \
 && pip install --no-cache-dir \
    --timeout 300 \
    --retries 20 \
    -r requirements.txt

COPY main.py .

RUN apt-get update && apt-get install -y cron
COPY cron /cron
RUN chmod +x /cron/run_2fa.sh \
 && chmod 0644 /cron/2fa-cron \
 && crontab /cron/2fa-cron


CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
