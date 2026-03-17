"""
apps/agent/memory_substrate.py — AG-Visio Memory Engine
Industrial-grade local RAG using LanceDB and FastEmbed.
Matches SOTA 2026 standards for reductionist data management.
"""

import json
import logging
import os
from typing import Any

import lancedb
from fastembed import TextEmbedding

logger = logging.getLogger("ag-visio-memory")


class MemorySubstrate:
    def __init__(self, db_path: str = "./lancedb_data"):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.embedding_model = TextEmbedding()

        # Initialize tables if they don't exist
        self._init_tables()

    def _init_tables(self):
        """Initialize LanceDB tables for different context types."""
        # Note: We use simple dicts for inference, but ensured types
        if "transcripts" not in self.db.table_names():
            self.db.create_table(
                "transcripts",
                data=[
                    {
                        "vector": [0.0] * 384,
                        "text": "init",
                        "speaker": "system",
                        "room_name": "init",
                        "timestamp": 0.0,
                    }
                ],
                mode="overwrite",
            )

        if "codebase" not in self.db.table_names():
            self.db.create_table(
                "codebase",
                data=[
                    {
                        "vector": [0.0] * 384,
                        "text": "init",
                        "file_path": "init",
                        "line_range": "init",
                        "metadata": "{}",
                    }
                ],
                mode="overwrite",
            )

        if "mission_logs" not in self.db.table_names():
            self.db.create_table(
                "mission_logs",
                data=[{"vector": [0.0] * 384, "text": "init", "status": "init", "timestamp": 0.0}],
                mode="overwrite",
            )

    def ingest_transcript(self, text: str, speaker: str, room_name: str = "default"):
        """Ingests a segment of conversation into the transcript table."""
        try:
            vector = list(next(self.embedding_model.embed([text])))
            table = self.db.open_table("transcripts")
            table.add(
                [
                    {
                        "vector": vector,
                        "text": text,
                        "speaker": speaker,
                        "timestamp": 0.0,  # Placeholder for real time
                        "room_name": room_name,
                    }
                ]
            )
            logger.info(f"Ingested transcript segment from {speaker}")
        except Exception as e:
            logger.error(f"Failed to ingest transcript: {e}")

    def query_history(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Queries past transcripts for relevant context."""
        try:
            vector = list(next(self.embedding_model.embed([query])))
            table = self.db.open_table("transcripts")
            results = table.search(vector).limit(limit).to_list()
            return results
        except Exception as e:
            logger.error(f"Query history failed: {e}")
            return []

    def index_project(self, root_dir: str):
        """Indexes the local repository logic and docs."""
        logger.info(f"Indexing project at {root_dir}...")
        code_table = self.db.open_table("codebase")

        data = []
        for root, _, files in os.walk(root_dir):
            if any(part in root for part in [".git", "venv", "__pycache__", "node_modules"]):
                continue

            for file in files:
                if file.endswith((".py", ".tsx", ".ts", ".md", ".txt")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, encoding="utf-8") as f:
                            content = f.read()
                            # Minimal chunking: by 1000 chars for now
                            chunks = [content[i : i + 1000] for i in range(0, len(content), 1000)]
                            for i, chunk in enumerate(chunks):
                                vector = list(next(self.embedding_model.embed([chunk])))
                                data.append(
                                    {
                                        "vector": vector,
                                        "text": chunk,
                                        "file_path": os.path.relpath(path, root_dir),
                                        "line_range": (
                                            f"{i * 20}-{(i + 1) * 20}"
                                        ),  # Loose approximation
                                        "metadata": json.dumps({"type": "code"}),
                                    }
                                )
                    except Exception as e:
                        logger.error(f"Failed to read {path}: {e}")

        if data:
            code_table.add(data)
            logger.info(f"Indexed {len(data)} chunks from {root_dir}")

    def query_codebase(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """Queries the codebase for relevant technical snippets."""
        try:
            vector = list(next(self.embedding_model.embed([query])))
            table = self.db.open_table("codebase")
            results = table.search(vector).limit(limit).to_list()
            return results
        except Exception as e:
            logger.error(f"Query codebase failed: {e}")
            return []


if __name__ == "__main__":
    # isolated test mode
    logging.basicConfig(level=logging.INFO)
    substrate = MemorySubstrate()
    # substrate.index_project(".") # Index self
    substrate.ingest_transcript("We should focus on corporate plans for summer.", "Sandra")
    res = substrate.query_history("summer plans")
    print(f"Transcript Query Results: {res}")

    technical_res = substrate.query_codebase("index_project")
    print(f"Codebase Query Results: {technical_res}")
