# Multi-stage build for Render (Frontend + Backend in one container)

# ----------------------------
# Stage 1: Build Frontend
# ----------------------------
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
# Build for production with relative API paths (empty string)
ENV VITE_API_URL=""
RUN npm run build

# ----------------------------
# Stage 2: Build Backend & Serve
# ----------------------------
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy Backend code
COPY backend/app ./app
COPY backend/logging_config.py .
# Copy Scraper code (needed for scheduler to import spiders)
COPY scraper/ ./scraper/
COPY scrapy.cfg .

# Copy Frontend build artifacts to backend static folder
COPY --from=frontend-build /app/frontend/dist ./app/static

# Create logs directory
RUN mkdir -p /app/logs

# Create empty DB file if not exists (will be overwritten by persistent disk if mounted)
RUN touch games_industry_jobs.db

# Expose port (Render sets PORT env var, default 10000)
ENV PORT=10000
EXPOSE 10000

# Start command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
