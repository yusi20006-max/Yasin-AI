"""#142 — HA/distributed persistence deferred (decision record)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ha_adr_defers_implementation():
    text = (ROOT / "docs" / "ADR_0011_DISTRIBUTED_HA.md").read_text(encoding="utf-8")
    assert "do not implement" in text.lower()
    assert "single-node" in text.lower()


def test_no_cluster_module_claimed():
    assert not (ROOT / "yasinai" / "cluster").exists()
    assert not (ROOT / "yasinai" / "ha").exists()
