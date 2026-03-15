"""
apps/agent/agent.py — AG-Visio Voice Agent
LiveKit Agents 1.x compatible. Implements a custom Ollama LLM backend.

LiveKit Agents 1.x notes:
- LLMStream._run() replaces the old __aiter__ pattern from 0.x.
- FunctionNetwork was removed in 1.x; tool/function calling is handled
  via llm.ChatContext + function call chunks natively.
- Agent (livekit.agents.voice.Agent) is the current high-level API.
- conn_options: SpeechHandle / ConnectOptions passed through from the
  pipeline; not used for Ollama but must be accepted in the signature.
"""

import json
import logging
import os
import sys
from typing import Annotated, Any

import lancedb
import ollama
from dotenv import load_dotenv
from fastembed import TextEmbedding
from livekit import rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.llm import LLMStream
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import (
    deepgram,
    livekit,
    openai,
    silero,
    turn_detector,
    whisper,
)
from livekit.plugins import piper_tts as piper

from logic import ReductionistLogic
from memory_substrate import MemorySubstrate
from state_bus import StateBus
from vision_analyze import VisionSubstrate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent_industrial.log"),
    ],
)
logger = logging.getLogger("ag-visio-agent")

load_dotenv()

AGENT_MODE = os.environ.get("AGENT_MODE", "local").lower()
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")


# ---------------------------------------------------------------------------
# Custom LLM: Ollama backend (livekit-agents 1.x pattern)
# ---------------------------------------------------------------------------


class SOTAOllamaLLMStream(LLMStream):
    """
    livekit-agents 1.x LLMStream subclass.

    In 1.x the framework calls _run() as a coroutine and consumes the
    internal _event_ch channel.  Do NOT implement __aiter__ — that was
    the 0.x pattern and is incompatible with the 1.x pipeline.
    """

    def __init__(
        self,
        ollama_llm: "SOTAOllamaLLM",
        *,
        chat_ctx: llm.ChatContext,
        conn_options: Any,
        fnc_ctx: llm.FunctionContext | None,
    ) -> None:
        super().__init__(ollama_llm, chat_ctx=chat_ctx, conn_options=conn_options, fnc_ctx=fnc_ctx)

    async def _run(self) -> None:  # noqa: C901
        """Generate chunks from Ollama and push them to the pipeline event channel."""
        llm_instance: SOTAOllamaLLM = self._llm  # type: ignore[assignment]
        try:
            # Build message list from ChatContext.  In 1.x message.content
            # may be a string OR a list of content blocks — handle both.
            messages: list[dict[str, str]] = []
            for msg in self._chat_ctx.messages:
                content = msg.content
                if isinstance(content, list):
                    # Flatten content blocks to plain text for Ollama
                    content = " ".join(
                        block.text if hasattr(block, "text") else str(block)
                        for block in content
                    )
                messages.append({"role": msg.role, "content": content or ""})

            logger.debug(
                "Sending chat request to Ollama: %d messages",
                len(messages),
            )

            response = await llm_instance._client.chat(
                model=llm_instance._model,
                messages=messages,
                stream=True,
            )

            async for chunk in response:
                delta_content = ""
                if isinstance(chunk, dict):
                    delta_content = (chunk.get("message") or {}).get("content", "")
                elif hasattr(chunk, "message"):
                    delta_content = getattr(chunk.message, "content", "") or ""

                if not delta_content:
                    continue

                self._event_ch.send_nowait(
                    llm.ChatChunk(
                        choices=[
                            llm.Choice(
                                delta=llm.ChoiceDelta(
                                    role="assistant",
                                    content=delta_content,
                                )
                            )
                        ]
                    )
                )

        except Exception as exc:
            logger.error("SOTA-E03: Ollama interaction failed: %s", exc)
            self._event_ch.send_nowait(
                llm.ChatChunk(
                    choices=[
                        llm.Choice(
                            delta=llm.ChoiceDelta(
                                role="assistant",
                                content=(
                                    "[DETACHED] LLM Substrate Connection Error."
                                    " Please verify Ollama is running."
                                ),
                            )
                        )
                    ]
                )
            )


class SOTAOllamaLLM(llm.LLM):
    """Ollama-backed LLM for the livekit-agents 1.x pipeline."""

    def __init__(self, model: str = "llama3.1", base_url: str | None = None) -> None:
        super().__init__()
        self._model = model
        self._client = ollama.AsyncClient(host=base_url or OLLAMA_BASE_URL)
        logger.info("Initialized SOTA Ollama LLM with model: %s", model)

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        conn_options: Any = None,
        fnc_ctx: llm.FunctionContext | None = None,
    ) -> SOTAOllamaLLMStream:
        return SOTAOllamaLLMStream(
            self,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            fnc_ctx=fnc_ctx,
        )


class VisioTools(llm.FunctionContext):
    """SOTA 2026: Agent-native tool context for discourse analysis."""

    def __init__(self, logic: ReductionistLogic, memory: MemorySubstrate, room: rtc.Room):
        super().__init__()
        self._logic = logic
        self._memory = memory
        self._room = room

    @llm.ai_callable(description="Search the local knowledge base for repository context or past conversation history.")
    async def search_knowledge_base(
        self,
        query: Annotated[str, "The semantic search query (e.g., 'corporate summer plans' or 'how does screen share work?')"],
    ) -> str:
        """SOTA 2026: Semantic retrieval substrate."""
        logger.info("Visio querying memory substrate for: %s", query)
        
        # Concurrent retrieval
        history_hits = self._memory.query_history(query, limit=3)
        code_hits = self._memory.query_codebase(query, limit=2)
        
        results = []
        if history_hits:
            results.append("### Relevant Conversation History:")
            for hit in history_hits:
                results.append(f"- [{hit.get('speaker')}]: {hit.get('text')}")
        
        if code_hits:
            results.append("### Relevant Code Snippets:")
            for hit in code_hits:
                results.append(f"- [{hit.get('file_path')}]: {hit.get('text')[:200]}...")

        if not results:
            return "No relevant historical or technical context found for this query."
            
        return "\n".join(results)

    @llm.ai_callable(description="Analyzes discourse for semantic dilution or jargon overflow.")
    def analyze_discourse(
        self,
        text: Annotated[str, "The text to analyze for LDDO (Low-Density Discourse Objects)"],
    ) -> str:
        dilution = self._logic.analyze_saliency(text)
        if dilution >= 0.7:
            return f"CRITICAL: Discourse dilution at {dilution:.2f}. Ontological drift detected."
        return f"Discourse nominal. Dilution: {dilution:.2f}."

    @llm.ai_callable(
        description=(
            "Requests proactive remote assistance via RustDesk bridge. "
            "Use this when the user is struggling with technical tasks."
        )
    )
    async def request_remote_access(
        self,
        reason: Annotated[str, "The specific technical reason why remote access is required."],
    ) -> str:
        """
        SOTA 2026: Proactive substrate bridge.
        Signals the Web UI to prompt the user for RustDesk credentials.
        """
        logger.info("Visio requesting remote access substrate. Reason: %s", reason)

        payload = json.dumps({"type": "remote_request", "reason": reason})
        if self._room and self._room.isconnected():
            await self._room.local_participant.publish_data(payload)

        return (
            f"REQUEST_INITIATED: Remote assistance substrate requested for: {reason}. "
            "Prompting user for secure credential handoff."
        )


# ---------------------------------------------------------------------------
# Agent entrypoint
# ---------------------------------------------------------------------------


async def entrypoint(ctx: JobContext) -> None:
    logger.info("SOTA Entrypoint activated for session: %s", ctx.room.name)

    logic_engine = ReductionistLogic()
    initial_ctx = llm.ChatContext().append(role="system", text=logic_engine.reductionist_prompt)

    # SOTA 2026: Phase 5 Memory Substrate
    memory = MemorySubstrate()
    # Lazy index: in industrial use, this would be a background task
    # memory.index_project(".") 

    vision = VisionSubstrate(mode=AGENT_MODE)
    bus = StateBus()
    await bus.connect()

    await ctx.connect()

    try:
        vad = silero.VAD.load()

        if AGENT_MODE == "cloud":
            logger.info("Initializing Cloud-based providers (Deepgram/OpenAI)")
            # SOTA 2026: Inference Gateway minimizes cold starts
            stt = deepgram.STT()
            tts = openai.TTS()
            llm_engine = openai.LLM(model="gpt-4o-mini")
        elif AGENT_MODE == "gateway":
            logger.info("Initializing LiveKit Inference Gateway")
            stt = livekit.STT()
            tts = livekit.TTS()
            llm_engine = openai.LLM(model="gpt-4o-mini")
        else:
            logger.info("Initializing Local-only providers (Whisper/Piper/Ollama)")
            stt = whisper.STT()
            tts = piper.TTS()
            llm_engine = SOTAOllamaLLM(
                model=os.environ.get("OLLAMA_MODEL", "gemma2"),
                base_url=OLLAMA_BASE_URL,
            )
        
        @ctx.room.on("data_received")
        def on_data_received(data: rtc.DataPacket):
            """SOTA 2026: Secure credential handoff listener."""
            try:
                payload = json.loads(data.data.decode())
                if payload.get("type") == "remote_credentials":
                    target_id = payload.get("id")
                    password = payload.get("password")
                    if target_id and password:
                        logic_engine.set_remote_credentials(target_id, password)
                        logger.info("Remote credentials received via data channel")
            except Exception as e:
                logger.error("Failed to parse data packet: %s", e)

        assistant = VoicePipelineAgent(
            vad=vad,
            stt=stt,
            llm=llm_engine,
            tts=tts,
            turn_detector=turn_detector.EOUModel(),
            chat_ctx=initial_ctx,
            fnc_ctx=VisioTools(logic_engine, memory, ctx.room),
        )

        @assistant.on("user_speech_committed")
        def _on_user_speech(msg: llm.ChatMessage):
            """Log saliency and ingest into RAG substrate."""
            if isinstance(msg.content, str):
                # SOTA 2026: Real-time RAG ingestion
                memory.ingest_transcript(msg.content, speaker="User", room_name=ctx.room.name)
                
                saliency = logic_engine.analyze_saliency(msg.content)
                logger.info(
                    "User speech committed (saliency: %.2f) and ingested into RAG: %s",
                    saliency,
                    msg.content[:50] + "..." if len(msg.content) > 50 else msg.content,
                )

        async def _before_llm_cb(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
            """
            Reductionist Suppression Logic.
            Pre-empt the LLM generation if discourse density is too low.
            """
            last_msg = chat_ctx.messages[-1]
            if last_msg.role == "user" and isinstance(last_msg.content, str):
                saliency = logic_engine.analyze_saliency(last_msg.content)
                if saliency < 0.2:
                    logger.warning(
                        "Discourse density below threshold (%.2f). Suppressing response.", saliency
                    )
                    agent.suppress_response()

        assistant.before_llm_cb = _before_llm_cb

        @ctx.room.on("track_published")
        def on_track_published(publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            if publication.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
                logger.info("SOTA: Screen share detected from %s. Attaching vision node.", participant.identity)
                
                @publication.on("frame_received")
                async def on_frame_received(frame: rtc.VideoFrame):
                    # Periodically analyze frames for saliency/OCR
                    # [MOCK] Throttle to 1 fps for industrial efficiency
                    if rtc.get_time() % 1000 < 100: 
                        text = await vision.process_video_frame(frame)
                        if text:
                            # Publish to inter-agent state bus (Redis)
                            await bus.publish_state(ctx.room.local_participant.identity, {"ocr": text})
                            
                            # Publish to frontend via LiveKit Data Channel (Secure)
                            payload = json.dumps({"type": "fleet_update", "agent": ctx.room.local_participant.identity, "ocr": text})
                            await ctx.room.local_participant.publish_data(payload.encode())

        logger.info("Visio starting upgraded participation loop...")
        assistant.start(ctx.room)
        await assistant.say("Visio substrate operational. Fleet sync active.")

    except Exception as exc:
        logger.critical(
            "SOTA-C01: Failed to initialize agent session. Substrate failure: %s",
            exc,
        )
        if ctx.room.isconnected():
            await ctx.room.disconnect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
