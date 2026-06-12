import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def temp_lancedb():
    """Local copy: root tests/conftest.py is out of scope for this directory
    (pytest conftest visibility is directory-based)."""
    import lancedb

    tmpdir = tempfile.mkdtemp()
    db = lancedb.connect(tmpdir)
    yield db
    import shutil

    shutil.rmtree(tmpdir, ignore_errors=True)
