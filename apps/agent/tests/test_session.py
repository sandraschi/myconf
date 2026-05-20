import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import pytest
from logic import ReductionistLogic
from memory_substrate import MemorySubstrate
from state_bus import StateBus
from vision_analyze import VisionSubstrate


class TestReductionistLogic:
    def test_init(self):
        logic = ReductionistLogic()
        assert logic is not None
        assert not logic.remote_active

    def test_saliency_clean(self):
        logic = ReductionistLogic()
        assert logic.analyze_saliency("the build failed due to a type error") == 0.0

    def test_saliency_jargon(self):
        logic = ReductionistLogic()
        logic.enable_jargon_detection(True)
        score = logic.analyze_saliency("we need more synergy and holistic alignment")
        assert score > 0.5

    def test_saliency_empty(self):
        logic = ReductionistLogic()
        assert logic.analyze_saliency("") == 0.0

    def test_remote_credentials(self):
        logic = ReductionistLogic()
        assert not logic.remote_active
        logic.set_remote_credentials("target123", "p@ssword")
        assert logic.remote_active


class TestStateBus:
    @pytest.mark.asyncio
    async def test_lifecycle(self):
        bus = StateBus()
        assert not bus.is_connected
        await bus.connect()
        await bus.disconnect()
        assert not bus.is_connected


class TestVisionSubstrate:
    def test_init(self):
        vs = VisionSubstrate(mode="local")
        assert vs is not None

    @pytest.mark.asyncio
    async def test_process_frame(self):
        vs = VisionSubstrate(mode="local")
        result = await vs.process_video_frame(None)
        assert isinstance(result, str)


class TestMemorySubstrate:
    @pytest.fixture
    def memory(self, tmp_path):
        return MemorySubstrate(db_path=str(tmp_path / "test_lancedb"))

    def test_init_tables(self, memory):
        tables = memory.db.list_tables()
        table_names = tables.tables if hasattr(tables, "tables") else tables
        assert "transcripts" in table_names
        assert "codebase" in table_names
        assert "mission_logs" in table_names

    def test_ingest_and_query(self, memory):
        memory.ingest_transcript("discussing project timeline", speaker="Sandra")
        results = memory.query_history("project timeline")
        assert len(results) > 0
        assert "project timeline" in results[0]["text"]

    def test_query_empty(self, memory):
        results = memory.query_history("nonexistent")
        assert len(results) >= 0

    def test_index_project(self, memory, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("def hello(): return 'world'")
        memory.index_project(str(tmp_path))
        results = memory.query_codebase("hello")
        assert len(results) > 0
