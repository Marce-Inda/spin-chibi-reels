FROM python:3.11-slim

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend source code
COPY backend /app/backend
COPY frontend /app/frontend

# Create output directory
RUN mkdir -p /app/output /app/assets

EXPOSE 7860

# Run FastAPI with Uvicorn on port 7860 (Hugging Face Spaces default port)
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
