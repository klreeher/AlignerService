# Use official slim Python image
FROM python:3.10-slim

# Set build arguments
ARG MFA_VERSION=2.2.17
ARG MFA_ZIP=montreal-forced-aligner_linux-x86_64.zip
ARG MFA_SHA=0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    sox \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies early for caching
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install gunicorn

# Download and verify Montreal Forced Aligner, then install
RUN curl -L -o mfa.zip https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v${MFA_VERSION}/${MFA_ZIP} \
 && echo "${MFA_SHA}  mfa.zip" | sha256sum -c - \
 && unzip mfa.zip -d /opt \
 && ln -s /opt/montreal-forced-aligner/bin/mfa /usr/local/bin/mfa \
 && mfa --help

# Copy application code
COPY . .

# Expose port (match Gunicorn bind)
EXPOSE 80

# Run Gunicorn as production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:80", "api.main:app"]
