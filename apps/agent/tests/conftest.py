"""Pytest configuration and fixtures for AG-Visio agent tests."""

import sys
from pathlib import Path

import pytest

# Ensure agent package is importable when running from repo root or apps/agent
_agent_root = Path(__file__).resolve().parent.parent
if str(_agent_root) not in sys.path:
    sys.path.insert(0, str(_agent_root))


@pytest.fixture
def sample_jargon_text():
    """Sample text containing LDDO/jargon for saliency tests."""
    return "We need to leverage synergy and align our paradigm for digital transformation."


@pytest.fixture
def clean_text():
    """Text with no jargon."""
    return "The build failed because the API returned 404."
