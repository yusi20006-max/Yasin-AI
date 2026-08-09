"""Shared pytest isolation for process-local test artifacts."""

import os
import tempfile
from pathlib import Path


_TEST_MEMORY_PATH = Path(tempfile.gettempdir()) / f"yasinai-tests-{os.getpid()}.db"
if _TEST_MEMORY_PATH.exists():
    _TEST_MEMORY_PATH.unlink()
os.environ["YASINAI_MEMORY_PATH"] = str(_TEST_MEMORY_PATH)
