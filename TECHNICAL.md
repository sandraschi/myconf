# AG-Visio Technical Reference

This document provides a deep dive into the underlying architecture, protocols, and technology stack of the AG-Visio suite.

## 1. Real-Time Communication (LiveKit)

AG-Visio utilizes [LiveKit](https://livekit.io/) as its primary RTC engine. 
- **Infrastructure**: Distributed via Docker Compose with a dedicated Redis instance for state management.
- **Protocols**: WebRTC for video/audio streams, WebSockets for room signaling.
- **Egress**: Used for session recording and external streaming when configured.

## 2. AI Voice Assistant (Visio)

The voice assistant is built on a modular "perception-action" loop using local-first models to prioritize privacy and low latency.

### Speech-to-Text (STT)
- **Engine**: OpenAI Whisper (via `transformers` or `faster-whisper`).
- **Processing**: Real-time audio chunking with Voice Activity Detection (VAD) to trigger inference.

### Large Language Model (LLM)
- **Engine**: [Ollama](https://ollama.com/) running on the local host.
- **Default Model**: `gemma2:9b` (recommended for its balance of reasoning and performance).
- **Context**: Managed via a sliding window to maintain character consistency.

### Text-to-Speech (TTS)
- **Engine**: [Piper](https://github.com/rhasspy/piper).
- **Quality**: ONNX-based high-speed synthesis with low CPU overhead.
- **Voice**: Standardized on neutral, high-clarity models.

## 3. Remote Assistance (RustDesk)

Remote support is embedded directly into the browser dashboard.
- **Integration**: Uses the RustDesk relay bridge to tunnel traffic via the host.
- **Security**: End-to-end encrypted sessions with local ID verification.

## 4. Hardware & System Monitoring (MCP)

AG-Visio implements the **Model Context Protocol (MCP)** to provide the assistant with environmental awareness.
- **Metrics**: Real-time tracking of GPU VRAM (for Ollama health), CPU load, and disk occupancy.
- **Git Integration**: Automated status reporting for the monorepo.
- **Extensibility**: Standardized JSON-RPC interface for adding new monitoring tools.

## 5. Persistence & Vector Search (RAG)

Searchable memory is implemented using a Retrieval-Augmented Generation (RAG) pattern.
- **Vector DB**: [LanceDB](https://lancedb.com/) for zero-config, disk-persisted vector storage.
- **Embeddings**: `fastembed` for local, high-speed text vectorization.
- **Search Logic**: Semantic similarity search against historical meeting transcripts and documentation.

---

[Back to main README](README.md)
