FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose Flask port
EXPOSE 5000

# Default Ollama URL (override via env)
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV PORT=5000

CMD ["python", "backend/app.py"]
