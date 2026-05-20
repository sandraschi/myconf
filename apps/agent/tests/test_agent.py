"""Unit tests for AG-Visio Agent core modules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic import ReductionistLogic


class TestReductionistLogic:
    def test_analyze_saliency_returns_zero_for_clean_text(self):
        logic = ReductionistLogic()
        result = logic.analyze_saliency("this is a normal technical discussion")
        assert result == 0.0

    def test_analyze_saliency_detects_jargon(self):
        logic = ReductionistLogic()
        logic.enable_jargon_detection(True)
        result = logic.analyze_saliency("we need more synergy and holistic alignment")
        assert result > 0.0

    def test_analyze_saliency_normalizes_to_one(self):
        logic = ReductionistLogic()
        logic.enable_jargon_detection(True)
        result = logic.analyze_saliency("synergy paradigm vibes holistic manifest digital transformation")
        assert result == 1.0

    def test_analyze_saliency_case_insensitive(self):
        logic = ReductionistLogic()
        logic.enable_jargon_detection(True)
        result = logic.analyze_saliency("SYNERGY is important")
        assert result > 0.0

    def test_jargon_weights_initialized(self):
        logic = ReductionistLogic()
        logic.enable_jargon_detection(True)
        assert logic._jargon_detection_enabled
