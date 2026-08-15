"""#141 — advanced routing is documented as not implemented."""
from __future__ import annotations

import inspect
from pathlib import Path

from yasinai.providers.router import ProviderRouter

ROOT = Path(__file__).resolve().parents[1]


def test_adr_defers_advanced_routing():
    text = (ROOT / "docs" / "ADR_0010_ADVANCED_ROUTING.md").read_text(encoding="utf-8")
    assert "defer implementation" in text.lower()
    assert "NOT CURRENTLY IMPLEMENTED" in text or "not implement" in text.lower()


def test_router_has_no_cost_or_health_apis():
    members = {name for name, _ in inspect.getmembers(ProviderRouter)}
    for forbidden in ("select_by_cost", "select_by_health", "load_balance", "health_registry"):
        assert forbidden not in members
