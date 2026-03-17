"""Industrial fixtures for AG-Visio testing scaffold."""

import shutil
import sys
from pathlib import Path

# Ensure agent package is importable BEFORE substrate imports
_agent_root = Path(__file__).resolve().parent.parent
if str(_agent_root) not in sys.path:
    sys.path.insert(0, str(_agent_root))

import lancedb
import pytest

from contacts_substrate import Contact, ContactManager


@pytest.fixture
def temp_lancedb(tmp_path):
    """Provides a fresh, isolated LanceDB instance for each test."""
    db_dir = tmp_path / "test_lancedb"
    db = lancedb.connect(db_dir)
    yield db
    # Cleanup after test session
    if db_dir.exists():
        shutil.rmtree(db_dir)


@pytest.fixture
def mock_contact_manager(tmp_path):
    """Provides a ContactManager using a temporary cache file."""
    cache_file = tmp_path / "test_contacts.json"
    manager = ContactManager(cache_path=str(cache_file))
    return manager


@pytest.fixture
def sample_contacts():
    """Returns a list of SOTA-aligned sample contacts."""
    return [
        Contact(id="test_1", name="Sandra Test", email="sandra@test.at", source="mock"),
        Contact(id="test_2", name="Benny GSD", source="mock"),
    ]
