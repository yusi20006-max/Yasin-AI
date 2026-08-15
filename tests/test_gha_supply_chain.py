"""#148 — GitHub Actions supply-chain hardening checks."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"


def test_gha_doc_exists():
    assert (ROOT / "docs" / "GHA_SUPPLY_CHAIN.md").is_file()


def test_workflows_use_official_actions_only():
    for path in WF.glob("*.yml"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "uses:" in line and not line.strip().startswith("#"):
                action = line.split("uses:")[1].strip()
                assert action.startswith("actions/"), f"{path.name}: non-official action {action}"


def test_checkout_disables_persist_credentials():
    for path in WF.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        if "actions/checkout@" in text:
            assert "persist-credentials: false" in text


def test_ci_permissions_are_read_only_default():
    ci = (WF / "ci.yml").read_text(encoding="utf-8")
    assert "permissions:" in ci
    assert "contents: read" in ci
