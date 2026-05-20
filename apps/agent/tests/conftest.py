import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tempfile

import pytest


@pytest.fixture
def temp_lancedb():
    import lancedb

    tmpdir = tempfile.mkdtemp()
    db = lancedb.connect(tmpdir)
    yield db
    import shutil

    shutil.rmtree(tmpdir, ignore_errors=True)
