"""Tests for AG-Visio voice agent. Run from apps/agent: pytest"""

from logic import ReductionistLogic


class TestReductionistLogic:
    """Tests for ReductionistLogic saliency and jargon detection."""

    def test_analyze_saliency_returns_zero_for_clean_text(self, clean_text):
        logic = ReductionistLogic()
        assert logic.analyze_saliency(clean_text) == 0.0

    def test_analyze_saliency_detects_jargon(self, sample_jargon_text):
        logic = ReductionistLogic()
        score = logic.analyze_saliency(sample_jargon_text)
        assert score > 0.0
        assert score <= 1.0

    def test_analyze_saliency_normalizes_to_one(self):
        logic = ReductionistLogic()
        # Multiple jargon terms can sum > 1; should be capped
        text = "synergy paradigm vibes holistic alignment manifest digital transformation"
        score = logic.analyze_saliency(text)
        assert score <= 1.0

    def test_analyze_saliency_case_insensitive(self):
        logic = ReductionistLogic()
        assert logic.analyze_saliency("SYNERGY") > 0
        assert logic.analyze_saliency("Synergy") > 0

    def test_jargon_weights_initialized(self):
        logic = ReductionistLogic()
        assert "synergy" in logic.jargon_weights
        assert "vibes" in logic.jargon_weights
        assert logic.jargon_weights["vibes"] == 0.8
