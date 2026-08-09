"""Tests for the deterministic repository security scanner."""

from pathlib import Path

from security_platform.scanner import SecurityScanner


def _policy_files(root: Path) -> None:
    (root / ".gitignore").write_text(".env\n*.key\n*.pem\n*.token\n", encoding="utf-8")
    (root / "SECURITY_TRUTH.md").write_text("security truth", encoding="utf-8")
    (root / "AGENTS.md").write_text("engineering policy", encoding="utf-8")


def test_scanner_clean_repository(tmp_path: Path) -> None:
    _policy_files(tmp_path)
    (tmp_path / "config.py").write_text("VALUE = 'safe'\n", encoding="utf-8")

    report = SecurityScanner(tmp_path).scan()

    assert report["status"] == "SECURE"
    assert report["failed_items"] == 0
    assert report["scanned_items"] >= 5


def test_secret_scan_detects_private_key(tmp_path: Path) -> None:
    _policy_files(tmp_path)
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    (tmp_path / "sample.py").write_text(f"PRIVATE = {marker!r}\n", encoding="utf-8")

    report = SecurityScanner(tmp_path).scan()

    assert report["status"] == "VULNERABLE"
    findings = [item for item in report["findings"] if item["id"] == "SEC_SECRET_001"]
    assert findings and findings[0]["passed"] is False
    assert findings[0]["severity"] == "critical"
    assert findings[0]["path"] == "sample.py"


def test_secret_policy_requires_common_patterns(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")

    finding = SecurityScanner(tmp_path).check_secret_policy()

    assert finding.passed is False
    assert "*.key" in finding.details


def test_scanner_accepts_complete_secret_policy(tmp_path: Path) -> None:
    _policy_files(tmp_path)
    scanner = SecurityScanner(tmp_path)

    assert scanner.check_secret_policy().passed is True
    assert scanner.check_policy_files().passed is True


def test_world_writable_file_is_rejected(tmp_path: Path) -> None:
    _policy_files(tmp_path)
    source = tmp_path / "sample.py"
    source.write_text("print('x')", encoding="utf-8")
    source.chmod(0o666)

    findings = SecurityScanner(tmp_path).check_file_permissions()

    assert any(not item.passed and item.id == "SEC_PERM_001" for item in findings)


def test_scanner_skips_vcs_and_generated_directories(tmp_path: Path) -> None:
    _policy_files(tmp_path)
    for dirname in (".git", "build", "dist", "__pycache__"):
        directory = tmp_path / dirname
        directory.mkdir()
        (directory / "leak.py").write_text(
            "TOKEN = 'ghp_abcdefghijklmnopqrstuvwxyz123456'\n", encoding="utf-8"
        )

    report = SecurityScanner(tmp_path).scan()

    assert report["status"] == "SECURE"
    assert report["failed_items"] == 0
