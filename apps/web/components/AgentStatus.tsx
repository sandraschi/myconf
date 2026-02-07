"use client";

import { useParticipants } from "@livekit/components-react";

export default function AgentStatus() {
  const participants = useParticipants();
  const agentParticipant = participants.find((p) => {
    if (p.isLocal) return false;
    if (p.identity.toLowerCase().includes("agent")) return true;
    try {
      const meta = p.metadata ? JSON.parse(p.metadata) : {};
      return meta.agent === true;
    } catch {
      return false;
    }
  });

  if (!agentParticipant) return null;

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-green-900/30 border border-green-700/50 rounded-lg text-sm">
      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      <span className="text-green-400">Agent active</span>
    </div>
  );
}
