"""#149 — public/private module enforcement."""
from __future__ import annotations

import importlib

from yasinai.private_modules import PRIVATE_MODULES, is_private_module


def test_private_modules_are_marked():
    for name in PRIVATE_MODULES:
        mod = importlib.import_module(name)
        assert getattr(mod, "YASINAI_PRIVATE_MODULE", False) is True


def test_is_private_helper():
    assert is_private_module("knowledge_platform.memory") is True
    assert is_private_module("yasinai.contracts") is False


def test_public_packages_not_marked_private():
    for name in ("yasinai", "yasinai.contracts", "yasinai.services"):
        mod = importlib.import_module(name)
        assert getattr(mod, "YASINAI_PRIVATE_MODULE", False) is False
