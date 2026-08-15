"""Ecosystem version compatibility matrix (#135)."""
from __future__ import annotations

from typing import TypedDict


class CompatEntry(TypedDict):
    consumer: str
    min_yasinai: str
    max_yasinai_exclusive: str
    contract: str


# Canonical matrix for platform 1.1.4 / contract v1
COMPATIBILITY_MATRIX: list[CompatEntry] = [
    {
        "consumer": "yasin-agent",
        "min_yasinai": "1.1.4",
        "max_yasinai_exclusive": "1.2.0",
        "contract": "v1",
    },
    {
        "consumer": "yasin-core",
        "min_yasinai": "1.1.4",
        "max_yasinai_exclusive": "1.2.0",
        "contract": "v1",
    },
    {
        "consumer": "yasin-cli",
        "min_yasinai": "1.1.4",
        "max_yasinai_exclusive": "1.2.0",
        "contract": "v1",
    },
]


def _parse(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split(".")[:3])


def is_compatible(consumer: str, yasinai_version: str) -> bool:
    """Return True if *yasinai_version* satisfies the matrix row for *consumer*."""
    key = consumer.lower().replace("_", "-")
    for row in COMPATIBILITY_MATRIX:
        if row["consumer"] != key:
            continue
        ver = _parse(yasinai_version)
        return _parse(row["min_yasinai"]) <= ver < _parse(row["max_yasinai_exclusive"])
    return False
