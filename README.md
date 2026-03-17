# myconf (AG-Visio)

**A professional video conferencing suite with an integrated AI assistant and remote collaboration tools.**

AG-Visio provides a complete environment for collaborative work, combining high-performance video communication with local-first AI and remote desktop support.

## Key Features

- **Video Conferencing**: Real-time multi-room video and audio powered by LiveKit 1.x / SDK v2.
- **AI Voice Assistant**: A local-first assistant ("Visio") with End-of-Utterance detection and multimodal tool use.
- **Remote Assistance**: Embedded RustDesk bridge and Agent-Mediated remote assistance tools.
- **Dynamic Layouts**: Intelligent focus mode and manual viewport promotion.
- **Long-term Memory**: High-performance semantic search and transcription RAG using **LanceDB** and **FastEmbed**.
- **Perception & Awareness**: Industrial OCR pipeline and multi-agent signaling for workspace intelligence.
- **Address Book Integration**: Searchable cross-platform contacts (Windows, Office 365, Gmail).
- **Industrial Quality**: Codebase standardized with **Ruff** and verified via an extensive **Pytest** scaffold.

---

## Quick Start

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/sandraschi/myconf.git
   cd myconf
   ```

2. **Run the orchestrator**:
   ```powershell
   .\start.bat
   ```

> [!TIP]
> **One-Click Initialization**: On the first run, `start.bat` automatically detects missing dependencies and executes the setup substrate (installing Node modules and Python environments) before launching the services.

## Documentation

For internal architecture, protocol details, and deep-dive technical information (LiveKit, AI Agent components, STT/TTS, and System Orchestration), please refer to the **[Technical Reference](TECHNICAL.md)**.

---

## Directory Structure

- **apps/web**: Next.js dashboard for video rooms and remote assistance.
- **apps/agent**: Python Voice Agent orchestrator (Visio).
- **apps/docs**: Technical documentation site.
- **packages/mcp-server**: System monitoring and Git metric tools.
- **infrastructure**: Deployment configuration (LiveKit/Redis).

---

## Configuration

### Environment Variables
Setup `apps/web/.env.local` for room connectivity:
```env
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:15580
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### AI Models (Ollama)
Visio requires [Ollama](https://ollama.com/) running on the host. We recommend the `gemma2` model.
```powershell
ollama pull gemma2
```

---

## License
MIT
