"""Shared pytest isolation for durable test artifacts."""

import os
import tempfile
from pathlib import Path


_BASE = Path(tempfile.gettempdir())
_TEST_MEMORY_PATH = _BASE / f"yasinai-tests-{os.getpid()}.db"
_TEST_VECTOR_PATH = _BASE / f"yasinai-vectors-{os.getpid()}.db"

for _path in (_TEST_MEMORY_PATH, _TEST_VECTOR_PATH):
    if _path.exists():
        _path.unlink()

os.environ["YASINAI_MEMORY_PATH"] = str(_TEST_MEMORY_PATH)
os.environ["YASINAI_VECTOR_PATH"] = str(_TEST_VECTOR_PATH)
