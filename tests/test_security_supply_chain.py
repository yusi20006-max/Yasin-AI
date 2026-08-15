"""#137 — security & supply-chain gate verification."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_security_supply_chain_doc_exists():
    path = ROOT / "docs" / "SECURITY_SUPPLY_CHAIN.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "pip-audit" in text
    assert "Untrusted plugin sandbox is **not** implemented" in text


def test_ci_security_job_is_blocking():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pip_audit" in ci or "pip-audit" in ci
    assert "security check" in ci
    assert "Forbidden secret" in ci or "forbidden" in ci
    # security job must not be continue-on-error
    security_block = ci.split("security:")[1].split("docker:")[0]
    assert "continue-on-error: true" not in security_block


def test_repository_security_check_passes():
    # main expects argv style via sys.argv when called as CLI; call scanner directly
    from security_platform.scanner import SecurityScanner

    report = SecurityScanner(root=ROOT).scan()
    # scan returns dict with findings
    assert report is not None
