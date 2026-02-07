"use client";

import { useConnectionState } from "@livekit/components-react";
import { Loader2 } from "lucide-react";

export default function ReconnectionBanner() {
  const state = useConnectionState();

  if (state !== "reconnecting" && state !== "connecting") return null;

  return (
    <div className="flex items-center justify-center gap-2 py-2 px-4 bg-amber-900/50 border-b border-amber-700/50 text-amber-200 text-sm">
      <Loader2 className="w-4 h-4 animate-spin" />
      {state === "reconnecting" ? "Reconnecting..." : "Connecting..."}
    </div>
  );
}
