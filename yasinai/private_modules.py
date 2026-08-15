"""Canonical list of private implementation packages (#149)."""
from __future__ import annotations

PRIVATE_MODULES: frozenset[str] = frozenset(
    {
        "knowledge_platform",
        "developer_platform",
        "security_platform",
    }
)


def is_private_module(name: str) -> bool:
    root = name.split(".")[0]
    return root in PRIVATE_MODULES
