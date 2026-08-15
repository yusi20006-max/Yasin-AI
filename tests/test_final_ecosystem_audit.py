"""#144 — final ecosystem audit verification."""
from __future__ import annotations

from pathlib import Path

import yasinai
from yasinai.contracts import CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "docs/PUBLIC_API_CONTRACT.md",
    "docs/ECOSYSTEM_COMPATIBILITY_MATRIX.md",
    "docs/API_ERROR_CONTRACT.md",
    "docs/SECURITY_SUPPLY_CHAIN.md",
    "docs/ARCHITECTURE_BOUNDARIES.md",
    "docs/PRODUCTION_READINESS.md",
    "docs/FINAL_ECOSYSTEM_AUDIT.md",
    "docs/ADR_0010_ADVANCED_ROUTING.md",
    "docs/ADR_0011_DISTRIBUTED_HA.md",
    "docs/ADR_0012_PLUGIN_TRUST.md",
]


def test_final_audit_doc_lists_limitations():
    text = (ROOT / "docs" / "FINAL_ECOSYSTEM_AUDIT.md").read_text(encoding="utf-8")
    assert "NOT IMPLEMENTED" in text or "PLANNED" in text
    assert "1.1.4" in text


def test_required_governance_docs_exist():
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).is_file()]
    assert not missing, missing


def test_platform_and_contract_versions():
    assert yasinai.__version__ == "1.1.4"
    assert CONTRACT_VERSION == "v1"
