# myconf (AG-Visio)

**A professional video conferencing suite with an integrated AI assistant and remote collaboration tools.**

AG-Visio provides a complete environment for collaborative work, combining high-performance video communication with local-first AI and remote desktop support.

## Key Features

- **Video Conferencing**: Real-time multi-room video and audio powered by LiveKit.
- **AI Voice Assistant**: A local-first assistant ("Visio") that joins rooms and assists via natural language.
- **Remote Assistance**: Embedded RustDesk bridge for seamless remote control support within the browser.
- **Dynamic Layouts**: Intelligent focus mode that automatically promotes active screen shares.
- **Memory & Search**: Searchable knowledge base and conversation history using local vector storage (LanceDB).
- **System Monitoring**: Comprehensive MCP server for monitoring hardware health, Git status, and system logs.

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

- **apps/web**: Next.js dashboard for video rooms, settings, and remote assistance (Port 15500).
- **apps/agent**: Python Voice Agent using Ollama, Whisper, and Piper.
- **apps/docs**: Technical documentation site (Port 15501).
- **packages/mcp-server**: Monitoring tools for hardware, disk, and Git metrics.
- **infrastructure**: Docker Compose configuration for LiveKit and Redis.

---

## Configuration

### Environment Variables
Create `apps/web/.env.local`:
```env
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:15580
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### AI Agent (Ollama)
The assistant requires [Ollama](https://ollama.com/) running on the host. We recommend the `gemma2` model:
```powershell
ollama pull gemma2
```

---

## Usage Controls

| Shortcut | Action |
| --- | --- |
| `?` | Open Help Modal |
| `Esc` | Close Modals |
| `Alt+R` | Toggle Remote Assistance Panel |

- **Log Viewer**: Accessible via the terminal icon in the topbar for real-time diagnostics.
- **Device Test**: Navigate to `/test` to verify camera and microphone levels before joining.

---

## Development

### Turborepo Commands
- `turbo build`: Build all components.
- `turbo dev`: Run the entire stack in development mode.
- `turbo dev --filter=web`: Run only the web application.

### Testing
- **Web (Next.js)**: `npm run test` (Vitest) or `npm run test:e2e` (Playwright).
- **Agent (Python)**: `pytest` within the `apps/agent` directory.

### MCP Tools
To use the monitoring tools in Claude Desktop, add the following to your configuration:
```json
"mcpServers": {
  "myconf": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/myconf", "run", "myconf"]
  }
}
```

---

## License
MIT
