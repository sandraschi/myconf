"""
Integration tests for the AG-Visio memory substrate.
"""

import os

import pytest
from memory_substrate import MemorySubstrate


class TestMemorySubstrate:
    """Verification of LanceDB and embedding logic."""

    @pytest.fixture
    def memory(self, temp_lancedb):
        test_path = temp_lancedb.uri
        return MemorySubstrate(db_path=test_path)

    def test_indexing_codebase_survives_empty_dir(self, memory, tmp_path):
        empty_dir = tmp_path / "empty_repos"
        os.makedirs(empty_dir)
        memory.index_project(str(empty_dir))
        table = memory.db.open_table("codebase")
        assert table.count_rows() == 1

    def test_search_logic_basic(self, memory, tmp_path):
        test_dir = tmp_path / "test_src"
        os.makedirs(test_dir)
        with open(test_dir / "app.py", "w") as f:
            f.write("def calculate_synergy(): return True")

        memory.index_project(str(test_dir))
        table = memory.db.open_table("codebase")
        assert table.count_rows() > 1

        results = memory.query_codebase("synergy")
        assert len(results) > 0
        assert "calculate_synergy" in results[0]["text"]

    def test_transcript_ingestion(self, memory):
        memory.ingest_transcript("Meeting about summer planning and digital transformation.", speaker="Sandra Schipal")
        results = memory.query_history("summer planning")
        assert len(results) > 0
        assert "summer planning" in results[0]["text"]
        assert results[0]["speaker"] == "Sandra Schipal"
        assert "Meeting about summer" in results[0]["text"]

    def test_multiple_transcripts(self, memory):
        memory.ingest_transcript("First discussion", speaker="Alice")
        memory.ingest_transcript("Second discussion", speaker="Bob")
        results = memory.query_history("discussion", limit=5)
        assert len(results) >= 2

    def test_codebase_embedding_consistency(self, memory, tmp_path):
        test_dir = tmp_path / "code_test"
        os.makedirs(test_dir)
        with open(test_dir / "server.py", "w") as f:
            f.write("import socket\n\ndef start_server():\n    return socket.socket()")

        memory.index_project(str(test_dir))
        results = memory.query_codebase("socket server")
        assert len(results) > 0
