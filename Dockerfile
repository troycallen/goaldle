# Use uv base image for faster dependency installation
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies using uv for speed
COPY requirements-railway.txt requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Set working directory to cv-api
WORKDIR /app/cv-api

# Expose port
EXPOSE 8001

# Start command
CMD ["python", "main.py"]
