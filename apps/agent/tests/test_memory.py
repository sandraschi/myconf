"""Integration tests for the AG-Visio memory substrate."""

import os

import pytest

from memory_substrate import MemorySubstrate


class TestMemorySubstrate:
    """Verification of LanceDB and embedding logic."""

    @pytest.fixture
    def memory(self, temp_lancedb):
        """Returns a MemorySubstrate initialized with temporary DB."""
        test_path = temp_lancedb.uri
        return MemorySubstrate(db_path=test_path)

    def test_indexing_codebase_survives_empty_dir(self, memory, tmp_path):
        """Ensures indexer doesn't crash on empty directories."""
        empty_dir = tmp_path / "empty_repos"
        os.makedirs(empty_dir)

        # Should not raise
        memory.index_project(str(empty_dir))

        # Verify table exists but only contains the 'init' row
        table = memory.db.open_table("codebase")
        assert table.count_rows() == 1

    def test_search_logic_basic(self, memory, tmp_path):
        """Tests that indexing and searching basic text works."""
        test_dir = tmp_path / "test_src"
        os.makedirs(test_dir)
        with open(test_dir / "app.py", "w") as f:
            f.write("def calculate_synergy(): return True")

        memory.index_project(str(test_dir))

        # Verify indexing
        table = memory.db.open_table("codebase")
        assert table.count_rows() > 1

        # Test search
        results = memory.query_codebase("synergy")
        assert len(results) > 0
        assert "calculate_synergy" in results[0]["text"]

    def test_transcript_ingestion(self, memory):
        """Verifies conversation history is being persisted to LanceDB."""
        memory.ingest_transcript(
            "Meeting about summer planning and digital transformation.",
            speaker="Sandra Schipal"
        )

        results = memory.query_history("summer planning")
        assert len(results) > 0
        assert "summer planning" in results[0]["text"]

        # Verify fields
        assert results[0]["speaker"] == "Sandra Schipal"
        assert "Meeting about summer" in results[0]["text"]
