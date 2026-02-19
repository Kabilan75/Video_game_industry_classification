FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc required for some python packages like uvicorn/uvloop compilation if wheels missing
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

# Using gunicorn/uvicorn worker for production readiness
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
