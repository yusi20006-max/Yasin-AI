"""#135 — machine-checkable ecosystem version compatibility matrix."""
from __future__ import annotations

from pathlib import Path

import yasinai
from yasinai.compatibility import COMPATIBILITY_MATRIX, is_compatible
from yasinai.contracts import CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_matrix_covers_required_consumers():
    names = {r["consumer"] for r in COMPATIBILITY_MATRIX}
    assert names >= {"yasin-agent", "yasin-core", "yasin-cli"}


def test_current_platform_is_compatible_with_all_consumers():
    for row in COMPATIBILITY_MATRIX:
        assert is_compatible(row["consumer"], yasinai.__version__)


def test_incompatible_versions_rejected():
    assert is_compatible("yasin-agent", "1.0.0") is False
    assert is_compatible("yasin-agent", "2.0.0") is False
    assert is_compatible("unknown-product", yasinai.__version__) is False


def test_contract_version_aligned():
    assert CONTRACT_VERSION == "v1"
    assert all(r["contract"] == "v1" for r in COMPATIBILITY_MATRIX)


def test_matrix_document_exists():
    path = ROOT / "docs" / "ECOSYSTEM_COMPATIBILITY_MATRIX.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Yasin-Agent" in text
    assert "1.1.4" in text
