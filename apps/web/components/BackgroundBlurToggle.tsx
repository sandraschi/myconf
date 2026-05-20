"use client";

import { useState, useCallback, useRef } from "react";
import { VideoOff, Video, Loader2 } from "lucide-react";
import { useLocalParticipant } from "@livekit/components-react";
import { Track } from "livekit-client";

export default function BackgroundBlurToggle() {
  const { localParticipant } = useLocalParticipant();
  const [isBlurred, setIsBlurred] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const processorRef = useRef<any>(null);

  const handleToggle = useCallback(async () => {
    if (isToggling) return;
    setIsToggling(true);
    try {
      if (isBlurred) {
        if (processorRef.current) {
          try { processorRef.current.disable(); } catch {}
          processorRef.current = null;
        }
        setIsBlurred(false);
      } else {
        const { BackgroundBlur } = await import("@livekit/track-processors");
        const pub = localParticipant?.getTrackPublication(Track.Source.Camera);
        const videoTrack = pub?.track;
        if (videoTrack && "setProcessor" in videoTrack) {
          const processor = BackgroundBlur();
          processorRef.current = processor;
          await (videoTrack as any).setProcessor(processor);
          setIsBlurred(true);
        }
      }
    } catch {
      // silently fail if processor not available
    } finally {
      setIsToggling(false);
    }
  }, [isBlurred, isToggling, localParticipant]);

  return (
    <button
      type="button"
      onClick={handleToggle}
      disabled={isToggling}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
        isBlurred
          ? "bg-purple-600 text-white hover:bg-purple-700"
          : "bg-neutral-800 text-gray-300 hover:bg-neutral-700"
      } disabled:opacity-50`}
      title={isBlurred ? "Disable background blur" : "Enable background blur"}
    >
      {isToggling ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : isBlurred ? (
        <VideoOff className="w-4 h-4" />
      ) : (
        <Video className="w-4 h-4" />
      )}
      <span className="hidden sm:inline">
        {isBlurred ? "Blur On" : "Blur"}
      </span>
    </button>
  );
}
