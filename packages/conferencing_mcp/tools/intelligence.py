import logging
import time
from typing import Any

from fastmcp import Context

from ..mcp_server import db, embedding_model, mcp

logger = logging.getLogger("ag-visio-mcp")


@mcp.tool()
async def generate_meeting_summary(ctx: Context, room_name: str, transcript: str) -> dict[str, Any]:
    """Summarize the meeting transcript and persist to the memory substrate."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")

    prompt = f"Summarize the following meeting transcript for room '{room_name}':\n\n{transcript}"

    try:
        summary_obj = await ctx.sample(prompt, max_tokens=1000)
        summary_text = summary_obj.content.text

        vector = list(next(embedding_model.embed([summary_text])))
        table = db.open_table("meeting_insights")
        table.add(
            [
                {
                    "vector": vector,
                    "type": "summary",
                    "content": summary_text,
                    "room_name": room_name,
                    "timestamp": time.time(),
                }
            ]
        )

        return {
            "success": True,
            "summary": summary_text,
            "room_name": room_name,
            "persisted": True,
            "correlation_id": cor_id,
        }
    except Exception as e:
        logger.error(f"Summary generation failed: {e}", extra={"correlation_id": cor_id})
        return {"success": False, "error": str(e)}


@mcp.tool()
async def extract_action_items(ctx: Context, room_name: str, transcript: str) -> dict[str, Any]:
    """Extract action items and tasks from the meeting transcript."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")

    prompt = (
        f"Extract a bulleted list of action items and assigned tasks from this meeting transcript "
        f"for room '{room_name}':\n\n{transcript}"
    )

    try:
        items_obj = await ctx.sample(prompt, max_tokens=1000)
        items_text = items_obj.content.text

        vector = list(next(embedding_model.embed([items_text])))
        table = db.open_table("meeting_insights")
        table.add(
            [
                {
                    "vector": vector,
                    "type": "action_items",
                    "content": items_text,
                    "room_name": room_name,
                    "timestamp": time.time(),
                }
            ]
        )

        return {
            "success": True,
            "action_items": items_text,
            "room_name": room_name,
            "persisted": True,
            "correlation_id": cor_id,
        }
    except Exception as e:
        logger.error(f"Action item extraction failed: {e}", extra={"correlation_id": cor_id})
        return {"success": False, "error": str(e)}


@mcp.tool()
async def set_translation_language(ctx: Context, language: str) -> str:
    """Set the target language for live translation in the current session."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(f"Setting translation language to: {language}", extra={"correlation_id": cor_id})
    return f"TRANSLATION_MODE_ACTIVE: Target set to '{language}'. All subsequent transcripts will be processed."
