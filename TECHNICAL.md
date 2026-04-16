# AG-Visio Technical Reference

This document provides a deep dive into the underlying architecture, protocols, and technology stack of the AG-Visio suite.

## 1. Real-Time Communication (LiveKit)

AG-Visio utilizes [LiveKit](https://livekit.io/) as its primary RTC engine. 
- **Infrastructure**: Distributed via Docker Compose with a dedicated Redis instance for state management.
- **Protocols**: WebRTC for video/audio streams, WebSockets for room signaling.
- **Teams++ Native Tracks**: High-fidelity screen capture via the `remoting-mcp` substrate, utilizing native `VideoTrack` publishing.
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

## 3. Remote Control Substrate (remoting-mcp)

AG-Visio 2.0 features a native remoting substrate that replaces the previous RustDesk IFrame bridge.
- **Implementation**: A specialized MCP server (`remoting-mcp`) running on the target PC.
- **Visuals**: Captures the primary monitor using `mss` and publishes it to the LiveKit room as a high-performance video track.
- **Input Injection**: Implements OS-level mouse and keyboard injection using the Windows `SendInput` API (via `pynput`).
- **Security**: Granular "Grant Access" workflow with explicit consent required for input substrate attachment.

## 4. Dynamic MCP Discovery & Intelligence

AG-Visio implements a decentralized **Model Context Protocol (MCP)** architecture.
- **Dynamic Discovery**: The agent performs a non-blocking scan of the 10700-10800 port range on startup to discover local SSE endpoints.
- **Combined Context**: Uses a `CombinedMCPFunctionContext` to unify local monitoring, remote control, and external tools (e.g., LiveKit Docs MCP).
- **Meeting Intelligence**: The `conferencing-mcp` server provides automated summarization and action item extraction, persisted to a **LanceDB** vector store for long-term recall.
- **Metrics**: Real-time tracking of GPU VRAM (for Ollama health), CPU load, and disk occupancy.

## 6. Multimodal Address Book

The VisioAgent supports a federated address book system that aggregates contacts across multiple providers.
- **Providers**: Microsoft Graph (Office 365), native Windows Contact store, and Gmail (Google People API).
- **Architecture**: A modular `AddressBookOrchestrator` manages provider discovery and result merging.
- **Search**: Integrated with the memory substrate for semantic contact retrieval using natural language.

## 7. Quality Engineering & Testing

AG-Visio adheres to high industrial standards for codebase health.
- **Linting**: Standardized on **Ruff** for Python analysis, ensuring zero architectural violations and consistent formatting.
- **Testing**: Comprehensive **Pytest** scaffold covering all core "brain" logic (Memory, Contacts, Agent tools).
- **Verification**: automated test cycles ensure 100% reliability of critical business logic before deployment.

---

[Back to main README](README.md)
