import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync } from "child_process";
import { RoomServiceClient } from "livekit-server-sdk";

const server = new Server(
    {
        name: "ag-visio-mcp",
        version: "0.1.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

const DEV_STATS_TOOL = {
    name: "get_dev_stats",
    description: "Get local development statistics (git status, disk usage)",
    inputSchema: {
        type: "object",
        properties: {},
    },
};

const SYSTEM_LOGS_TOOL = {
    name: "query_system_logs",
    description: "Query system logs for specific patterns",
    inputSchema: {
        type: "object",
        properties: {
            pattern: { type: "string" },
            limit: { type: "number", default: 10 },
        },
        required: ["pattern"],
    },
};

const LIVEKIT_ROOM_LIST_TOOL = {
    name: "livekit_room_list",
    description: "List active LiveKit rooms and participant counts. Requires LIVEKIT_URL (http), LIVEKIT_API_KEY, LIVEKIT_API_SECRET in env.",
    inputSchema: {
        type: "object",
        properties: {},
    },
};

server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [DEV_STATS_TOOL, SYSTEM_LOGS_TOOL, LIVEKIT_ROOM_LIST_TOOL],
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    switch (request.params.name) {
        case "get_dev_stats": {
            try {
                const gitStatus = execSync("git status --short").toString();
                const isWin = process.platform === "win32";
                const diskUsage = isWin
                    ? execSync('powershell -Command "Get-PSDrive C | Select-Object Used, Free"').toString()
                    : execSync("df -h .").toString();
                return {
                    content: [{ type: "text", text: `--- GIT STATUS ---\n${gitStatus}\n--- DISK STATUS ---\n${diskUsage}` }],
                };
            } catch (error: unknown) {
                const msg = error instanceof Error ? error.message : String(error);
                return { content: [{ type: "text", text: `Error: ${msg}` }], isError: true };
            }
        }
        case "query_system_logs": {
            const args = request.params.arguments as { pattern: string; limit?: number };
            const limit = args?.limit ?? 10;
            try {
                const cmd = `Get-EventLog -LogName System -Newest 100 | Where-Object { $_.Message -match "${args.pattern}" } | Select-Object -First ${limit} | Format-List Message`;
                const logs = execSync(`powershell -Command "${cmd}"`).toString();
                return {
                    content: [{ type: "text", text: logs || "No matching logs found." }],
                };
            } catch (error: unknown) {
                const msg = error instanceof Error ? error.message : String(error);
                return { content: [{ type: "text", text: `Error: ${msg}` }], isError: true };
            }
        }
        case "livekit_room_list": {
            const url = process.env.LIVEKIT_URL ?? "http://localhost:7880";
            const apiKey = process.env.LIVEKIT_API_KEY ?? "devkey";
            const apiSecret = process.env.LIVEKIT_API_SECRET ?? "secret";
            const httpUrl = url.startsWith("ws") ? url.replace(/^ws/, "http") : url;
            try {
                const roomService = new RoomServiceClient(httpUrl, apiKey, apiSecret);
                const rooms = await roomService.listRooms();
                const lines = rooms.length === 0
                    ? ["No active rooms."]
                    : rooms.map((r) => `${r.name} (${r.numParticipants} participants)`);
                return {
                    content: [{ type: "text", text: lines.join("\n") }],
                };
            } catch (error: unknown) {
                const msg = error instanceof Error ? error.message : String(error);
                return { content: [{ type: "text", text: `LiveKit error: ${msg}` }], isError: true };
            }
        }
        default:
            throw new Error("Tool not found");
    }
});

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}

main().catch(console.error);
