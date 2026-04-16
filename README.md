# myconf (AG-Visio)

**A modern video conferencing framework with integrated AI assistance and remote collaboration tools.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1.1+%2B-green.svg)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

AG-Visio provides a complete environment for collaborative work, combining high-performance video communication with local-first AI and remote desktop support.

## Key Features

- **Teams++ AI Integration**: v2.0.0 architecture update with LiveKit 1.0+ and Dynamic MCP tool discovery.
- **AI Voice Assistant**: Local-first assistant ("Visio") with autonomous multimodal tool execution.
- **Native Remoting Interface**: High-performance remoting via `remoting-mcp`, replacing the legacy RustDesk bridge.
- **Meeting Intelligence Dashboard**: Real-time insights panel with LanceDB-powered persistence for summaries and action items.
- **Persistent Vector Storage**: Secure RAG substrate using **LanceDB** and **FastEmbed**.
- **OCR & Event Signaling**: Modern OCR pipeline and multi-agent signaling for workspace analysis.
- **Modern Quality Standards**: Codebase standardized with **Ruff** and verified via a comprehensive **Pytest** scaffold.

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

- **[Technical Reference](TECHNICAL.md)**: Internal architecture, protocol details (LiveKit, AI Agent components), and system orchestration.
- **[Contributing Guide](CONTRIBUTING.md)**: Standards and processes for contributing to the monorepo.

---

## Directory Structure

- **apps/web**: Next.js dashboard featuring the `MeetingIntelligencePanel`.
- **apps/agent**: Python Voice Agent orchestrator (Visio) with dynamic MCP discovery.
- **packages/remoting-mcp**: Native remoting interface for screen capture and input injection.
- **packages/conferencing-mcp**: Meeting intelligence tools (summary/action items).
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
