import { RoomServiceClient } from "livekit-server-sdk";
import { NextRequest, NextResponse } from "next/server";

const LIVEKIT_PORT = 7880;

function getLiveKitHttpUrl(request: NextRequest): string {
  const forwarded = request.headers.get("x-forwarded-host");
  const host = forwarded || request.headers.get("host") || "localhost";
  const hostname = host.split(":")[0] ?? "localhost";
  return `http://${hostname}:${LIVEKIT_PORT}`;
}

export async function GET(request: NextRequest) {
  const apiKey = process.env.LIVEKIT_API_KEY || "devkey";
  const apiSecret = process.env.LIVEKIT_API_SECRET || "secret";
  const httpUrl = getLiveKitHttpUrl(request);

  try {
    const roomService = new RoomServiceClient(httpUrl, apiKey, apiSecret);
    const rooms = await roomService.listRooms();
    return NextResponse.json({
      status: "ok",
      livekit: { reachable: true, roomCount: rooms.length },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "degraded",
        livekit: { reachable: false, error: String(error) },
        timestamp: new Date().toISOString(),
      },
      { status: 503 }
    );
  }
}
