import logging
import os
import sys

import ollama
from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import piper, silero, whisper

from logic import ReductionistLogic

# SOTA Industrial Logging
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

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")


class SOTAOllamaLLM(llm.LLM):
    def __init__(self, model: str = "llama3.1", base_url: str | None = None):
        base_url = base_url or OLLAMA_BASE_URL
        super().__init__()
        self._model = model
        self._client = ollama.AsyncClient(host=base_url.replace("/v1", ""))
        logger.info(f"Initialized SOTA Ollama LLM with model: {model}")

    async def chat(self, history: list[llm.ChatMessage]):
        try:
            messages = [{"role": m.role, "content": m.content} for m in history]
            logger.debug(f"Sending chat request to Ollama: {len(messages)} messages")

            response = await self._client.chat(model=self._model, messages=messages, stream=True)

            async for chunk in response:
                if chunk.get("message") and chunk["message"].get("content"):
                    yield llm.ChatChunk(
                        choices=[
                            llm.Choice(
                                delta=llm.ChatMessage(
                                    role="assistant",
                                    content=chunk["message"]["content"],
                                )
                            )
                        ]
                    )
        except Exception as e:
            logger.error(f"SOTA-E03: Ollama interaction failed: {str(e)}")
            yield llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChatMessage(
                            role="assistant",
                            content="[DETACHED] LLM Substrate Connection Error.",
                        )
                    )
                ]
            )

    def create_context(self):
        return llm.ChatContext()


async def entrypoint(ctx: JobContext):
    logger.info(f"SOTA Entrypoint activated for session: {ctx.room.name}")

    logic_engine = ReductionistLogic()
    initial_ctx = llm.ChatContext().append(role="system", text=logic_engine.reductionist_prompt)

    try:
        # SOTA Plugin Scaffolding
        vad = silero.VAD.load()
        stt = whisper.STT()
        tts = piper.TTS()
        llm_engine = SOTAOllamaLLM(model=os.environ.get("OLLAMA_MODEL", "gemma2"))

        agent = VoicePipelineAgent(
            vad=vad,
            stt=stt,
            llm=llm_engine,
            tts=tts,
            chat_ctx=initial_ctx,
        )

        @agent.on("user_speech_committed")
        def on_speech(msg: llm.ChatMessage):
            text = msg.content
            dilution = logic_engine.analyze_saliency(text)

            # Reticence Logic
            if "visio" in text.lower() or dilution >= 0.7:
                logger.info("Visio triggered by high-entropy input.")
                if dilution >= 0.7 and "visio" not in text.lower():
                    agent.chat_ctx.append(
                        role="system",
                        text="[REFUTATION MODE] Address the ontological drift immediately.",
                    )
            else:
                logger.debug("Visio maintaining industrial silence.")

        logger.info("Visio starting participation loop...")
        agent.start(ctx.room)
        await agent.say("Visio substrate operational. Monitoring for LDDO.")

    except Exception as e:
        logger.critical(f"SOTA-C01: Failed to initialize agent session. {str(e)}")
        await ctx.room.disconnect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
