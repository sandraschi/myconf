# AG-Visio Voice Agent - full dockerization
FROM python:3.11-slim

WORKDIR /app

# System deps for audio/onnx (silero, whisper, piper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py logic.py ./

# LiveKit URL and keys set at runtime.
# Ollama runs OUTSIDE Docker on the host PC; agent reaches it via host.docker.internal.
ENV LIVEKIT_URL=ws://livekit:15580
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
ENV OLLAMA_MODEL=gemma2

CMD ["python", "agent.py", "dev"]
