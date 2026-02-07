import { AccessToken } from "livekit-server-sdk";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
    try {
        const { roomName, participantName } = await request.json();

        if (!roomName || !participantName) {
            return NextResponse.json(
                { error: "Missing roomName or participantName" },
                { status: 400 }
            );
        }

        const apiKey = process.env.LIVEKIT_API_KEY || "devkey";
        const apiSecret = process.env.LIVEKIT_API_SECRET || "secret";

        const at = new AccessToken(apiKey, apiSecret, {
            identity: participantName,
        });

        at.addGrant({
            room: roomName,
            roomJoin: true,
            canPublish: true,
            canSubscribe: true,
        });

        return NextResponse.json({ token: await at.toJwt() });
    } catch (error) {
        console.error("Token generation error:", error);
        return NextResponse.json(
            { error: "Internal Server Error" },
            { status: 500 }
        );
    }
}
