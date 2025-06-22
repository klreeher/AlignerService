# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed by MFA or Flask)
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    sox \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default run command
CMD ["python", "api/main.py"]
