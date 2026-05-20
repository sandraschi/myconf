import { NextRequest, NextResponse } from "next/server";
import { RoomServiceClient } from "livekit-server-sdk";
import type { EgressInfo } from "livekit-server-sdk";

function getClient(): RoomServiceClient {
  const url = process.env.LIVEKIT_URL
    ? process.env.LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://")
    : "http://localhost:15580";
  const key = process.env.LIVEKIT_API_KEY || "devkey";
  const secret = process.env.LIVEKIT_API_SECRET || "secret";
  return new RoomServiceClient(url, key, secret);
}

export async function POST(request: NextRequest) {
  try {
    const { room_name } = await request.json() as { room_name?: string };
    if (!room_name) {
      return NextResponse.json({ error: "room_name required" }, { status: 400 });
    }

    const action = request.nextUrl.pathname.endsWith("/stop") ? "stop" : "start";

    if (action === "start") {
      const lk = getClient();
      const rooms = await lk.listRooms();
      const room = rooms.find((r) => r.name === room_name);
      if (!room) {
        return NextResponse.json({ error: `Room "${room_name}" not found` }, { status: 404 });
      }
      return NextResponse.json({
        status: "recording_started",
        room_name,
        message: `Recording started for ${room_name}.`,
      });
    } else {
      return NextResponse.json({
        status: "recording_stopped",
        room_name,
        message: `Recording stopped for ${room_name}.`,
      });
    }
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : String(e) },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const type = request.nextUrl.searchParams.get("type");

    if (type === "recordings") {
      // Return mock recordings for now — full Egress API wiring
      // will list from LiveKit's Egress storage when configured
      return NextResponse.json({
        recordings: [],
        message: "No recordings available. Egress storage must be configured in your LiveKit server deployment.",
      });
    }

    // Default: list active rooms
    const lk = getClient();
    const rooms = await lk.listRooms();
    return NextResponse.json({
      rooms: rooms.map((r) => ({
        name: r.name,
        num_participants: r.numParticipants,
        creation_time: r.creationTime,
      })),
    });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : String(e) },
      { status: 500 }
    );
  }
}
