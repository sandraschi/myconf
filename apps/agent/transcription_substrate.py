"""
apps/agent/transcription_substrate.py — Multi-participant transcription.
Subscribes to every participant's audio track and runs independent STT.
Broadcasts final transcripts via LiveKit data channel.
"""

import asyncio
import json
import logging
from typing import Any

from livekit import rtc
from livekit.agents.stt import SpeechEventType

logger = logging.getLogger("ag-visio-transcription")


def _create_stt(mode: str):
    """Lazy-create an STT instance. Falls back to no-op if no plugin available."""
    try:
        if mode == "cloud":
            from livekit.plugins import deepgram

            return deepgram.STT()
        else:
            from livekit.plugins import openai

            return openai.STT(model="whisper-1")
    except (ImportError, Exception) as e:
        logger.warning("STT plugin not available (%s) — transcription disabled", e)
        return None


class TranscriptionSubstrate:
    """
    One STT stream per participant. When a participant subscribes an audio
    track, we create a dedicated STT stream and push frames through it.
    Final transcripts are broadcast to the room as data-channel messages
    that the dashboard's TranscriptionFeed component renders.
    """

    def __init__(self, room: rtc.Room, mode: str = "local"):
        self._room = room
        self._mode = mode
        self._streams: dict[str, Any] = {}  # participant_identity -> STTStream
        self._tasks: dict[str, asyncio.Task] = {}
        self._stopped = False

    async def start(self):
        """Subscribe to all existing and future audio tracks."""
        logger.info("Transcription substrate starting (%s mode)...", self._mode)

        # Subscribe to already-published tracks
        for participant in self._room.remote_participants.values():
            for pub in participant.track_publications.values():
                if pub.source == rtc.TrackSource.SOURCE_MICROPHONE:
                    track = pub.track
                    if track:
                        self._start_participant_transcription(participant.identity, track)

        # Listen for new subscriptions
        @self._room.on("track_subscribed")
        def _on_track_subscribed(
            track: rtc.Track,
            publication: rtc.TrackPublication,
            participant: rtc.Participant,
        ):
            if track.kind == "audio" and participant.identity != self._room.local_participant.identity:
                logger.info("New audio track from %s — starting STT", participant.identity)
                self._start_participant_transcription(participant.identity, track)

        # Clean up when participants leave
        @self._room.on("participant_disconnected")
        def _on_participant_disconnected(participant: rtc.Participant):
            self._stop_participant_transcription(participant.identity)

        logger.info(
            "Transcription substrate active — monitoring %d participant(s)", len(self._room.remote_participants)
        )

    def _start_participant_transcription(self, identity: str, track: rtc.Track):
        """Create an STT stream for one participant and start consuming frames."""
        if identity in self._streams:
            return

        stt = _create_stt(self._mode)
        if stt is None:
            return  # Don't register this participant if STT unavailable

        stt_stream = stt.stream()
        self._streams[identity] = stt_stream

        async def _run():
            try:
                audio_stream = rtc.AudioStream(track)

                # Pipeline: audio frames → STT → broadcast
                async def _push_frames():
                    async for frame in audio_stream:
                        if self._stopped or identity not in self._streams:
                            break
                        stt_stream.push_frame(frame)

                async def _collect_transcripts():
                    async for event in stt_stream:
                        if self._stopped:
                            break
                        if event.type == SpeechEventType.FINAL_TRANSCRIPT:
                            for alt in event.alternatives:
                                text = alt.text.strip()
                                if text:
                                    await self._broadcast_transcript(identity, text)

                await asyncio.gather(_push_frames(), _collect_transcripts())
            except Exception as e:
                if not self._stopped:
                    logger.debug("STT stream ended for %s: %s", identity, e)
            finally:
                self._cleanup(identity)

        self._tasks[identity] = asyncio.create_task(_run())
        logger.info("STT stream started for %s", identity)

    def _stop_participant_transcription(self, identity: str):
        self._cleanup(identity)

    def _cleanup(self, identity: str):
        if identity in self._streams:
            try:
                self._streams[identity].end_input()
            except Exception:
                logger.debug("Failed to end STT stream input", exc_info=True)
            del self._streams[identity]
        if identity in self._tasks:
            self._tasks[identity].cancel()
            del self._tasks[identity]

    async def _broadcast_transcript(self, identity: str, text: str):
        """Send transcript to all room participants via data channel."""
        if not self._room or not self._room.isconnected():
            return
        payload = json.dumps(
            {
                "type": "transcription",
                "speaker": identity,
                "transcript": text,
                "timestamp": __import__("time").time(),
            }
        )
        try:
            await self._room.local_participant.publish_data(payload.encode("utf-8"))
        except Exception as e:
            logger.debug("Broadcast failed: %s", e)

    async def stop(self):
        """Shut down all STT streams."""
        self._stopped = True
        for identity in list(self._streams.keys()):
            self._cleanup(identity)
        logger.info("Transcription substrate stopped")
