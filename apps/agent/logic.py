"""Lightweight meeting analysis utilities. No LiveKit dependency."""

import logging

logger = logging.getLogger("ag-visio-agent")


class ReductionistLogic:
    def __init__(self):
        self._remote_target_id = None
        self._remote_password = None
        self._jargon_detection_enabled = False  # opt-in via env
        logger.info("Meeting analysis engine initialized (jargon detection: disabled).")

    @property
    def remote_active(self) -> bool:
        return self._remote_target_id is not None

    def set_remote_credentials(self, target_id: str, password: str):
        self._remote_target_id = target_id
        self._remote_password = password
        logger.info("Remote credentials loaded for target %s", target_id)

    def analyze_saliency(self, text: str) -> float:
        """Analyze text for jargon density. Returns 0 unless enabled."""
        if not self._jargon_detection_enabled:
            return 0.0
        weights = {
            "synergy": 0.5,
            "paradigm": 0.4,
            "vibes": 0.8,
            "holistic": 0.6,
            "alignment": 0.3,
            "manifest": 0.7,
        }
        text_lower = text.lower()
        score = sum(w for j, w in weights.items() if j in text_lower)
        dilution = min(score, 1.0)
        if dilution > 0.0:
            logger.info(f"Jargon detected: {text[:50]}... Score: {dilution:.2f}")
        return dilution

    def enable_jargon_detection(self, enabled: bool = True):
        """Toggle jargon detection. Off by default."""
        self._jargon_detection_enabled = enabled
        logger.info("Jargon detection %s", "enabled" if enabled else "disabled")
