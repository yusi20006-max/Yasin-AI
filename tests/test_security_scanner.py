from pathlib import Path

from security_platform.scanner import SecurityScanner


def test_secret_scan_detects_private_key(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".env\n*.key\n*.pem\n*.token\n", encoding="utf-8")
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    (tmp_path / "sample.py").write_text(f"PRIVATE = {marker!r}\n", encoding="utf-8")
    report = SecurityScanner(tmp_path).scan()
    assert report["status"] == "VULNERABLE"
    assert any(item["id"] == "SEC_SECRET_001" and not item["passed"] for item in report["findings"])


def test_secret_policy_requires_common_patterns(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    finding = SecurityScanner(tmp_path).check_secret_policy()
    assert finding.passed is False
    assert "*.key" in finding.details


def test_scanner_accepts_complete_secret_policy(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".env\n*.key\n*.pem\n*.token\n", encoding="utf-8")
    (tmp_path / "SECURITY_TRUTH.md").write_text("security truth", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("policy", encoding="utf-8")
    scanner = SecurityScanner(tmp_path)
    assert scanner.check_secret_policy().passed is True
    assert scanner.check_policy_files().passed is True


def test_world_writable_file_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text("print('x')", encoding="utf-8")
    (tmp_path / "sample.py").chmod(0o666)
    findings = SecurityScanner(tmp_path).check_file_permissions()
    assert any(not item.passed and item.id == "SEC_PERM_001" for item in findings)
