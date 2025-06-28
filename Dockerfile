FROM python:3.10-slim

# Set working directory
WORKDIR /app

ENV PYTHONPATH=/app

# Install system dependencies for your audio tools
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    sox \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Default command — adjust later for gunicorn or uvicorn if you switch frameworks
CMD ["python", "api/main.py"]
