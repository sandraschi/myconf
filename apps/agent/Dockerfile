# AG-Visio Voice Agent — full dockerization
# Build from repo root: docker build -f apps/agent/Dockerfile -t myconf-agent .
FROM python:3.12-slim

WORKDIR /app

# System deps for audio/onnx, OCR, and screen capture
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY apps/agent/requirements.docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all agent source files
COPY apps/agent/agent.py apps/agent/logic.py apps/agent/memory_substrate.py \
     apps/agent/contacts_substrate.py apps/agent/state_bus.py \
     apps/agent/vision_analyze.py apps/agent/transcription_substrate.py ./

# Copy shared myconf package from repo root
COPY myconf/ /app/myconf/

# LiveKit URL and keys set at runtime.
# Ollama runs OUTSIDE Docker on the host PC; agent reaches it via host.docker.internal.
ENV LIVEKIT_URL=ws://livekit:15580
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
ENV OLLAMA_MODEL=gemma2

CMD ["python", "agent.py", "dev"]
