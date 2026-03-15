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

import logging
import os
import sys
from typing import Any

import ollama
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.agents.llm import LLMStream
from livekit.agents.voice import Agent
from livekit.plugins import piper_tts as piper
from livekit.plugins import silero
from livekit.plugins.openai import STT  # faster-whisper via livekit-plugins-openai

from logic import ReductionistLogic

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

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


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


# ---------------------------------------------------------------------------
# Agent entrypoint
# ---------------------------------------------------------------------------


async def entrypoint(ctx: JobContext) -> None:
    logger.info("SOTA Entrypoint activated for session: %s", ctx.room.name)

    logic_engine = ReductionistLogic()
    initial_ctx = llm.ChatContext().append(role="system", text=logic_engine.reductionist_prompt)

    await ctx.connect()

    try:
        vad = silero.VAD.load()
        stt = STT()  # faster-whisper via livekit-plugins-openai
        tts = piper.TTS()
        llm_engine = SOTAOllamaLLM(
            model=os.environ.get("OLLAMA_MODEL", "gemma2"),
            base_url=OLLAMA_BASE_URL,
        )

        assistant = Agent(
            vad=vad,
            stt=stt,
            llm=llm_engine,
            tts=tts,
            chat_ctx=initial_ctx,
        )

        @assistant.on("agent_speech_committed")
        def on_speech(msg: llm.ChatMessage) -> None:
            text = msg.content if isinstance(msg.content, str) else ""
            dilution = logic_engine.analyze_saliency(text)
            logger.info("Visio response saliency: %.2f", 1 - dilution)

            if "visio" in text.lower() or dilution >= 0.7:
                logger.info("Visio triggered by high-entropy input.")
                if dilution >= 0.7 and "visio" not in text.lower():
                    assistant.chat_ctx.append(
                        role="system",
                        text="[REFUTATION MODE] Address the ontological drift immediately.",
                    )
            else:
                logger.debug("Visio maintaining industrial silence.")

        logger.info("Visio starting participation loop...")
        assistant.start(ctx.room)
        await assistant.say("Visio substrate operational. Monitoring for LDDO.")

    except Exception as exc:
        logger.critical(
            "SOTA-C01: Failed to initialize agent session. Substrate failure: %s",
            exc,
        )
        if ctx.room.isconnected():
            await ctx.room.disconnect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
