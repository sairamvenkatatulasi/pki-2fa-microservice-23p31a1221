FROM python:3.12-slim AS base

# Install cron and curl
RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*

# Work inside /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1



# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py crypto_utils.py ./

# Copy cron files from local cron/ -> /app/cron
COPY cron/ /app/cron/

# Copy keys and other needed files
COPY student_public.pem student_private.pem instructor_public.pem ./
COPY .gitattributes .gitignore README.md ./

# Directory for cron log file
RUN mkdir -p /cron

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Install crontab from /app/cron/2fa-cron
RUN crontab /app/cron/2fa-cron

# Ensure script is executable
RUN chmod +x /app/cron/run_2fa.sh

EXPOSE 8080

CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
