"""Tests for yasinai.cli.security_entrypoint."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from yasinai.cli.security_entrypoint import main, security_check


def test_security_check_text_output(capsys):
    fake_report = {
        "status": "PASS",
        "findings": [
            {
                "name": "no_secrets",
                "passed": True,
                "severity": "high",
                "details": "clean",
                "path": None,
            }
        ],
        "scanned_items": 1,
        "failed_items": 0,
    }
    with patch("security_platform.scanner.SecurityScanner") as cls:
        cls.return_value.scan.return_value = fake_report
        code = security_check([])
    assert code == 0
    out = capsys.readouterr().out
    assert "PASS" in out or "Status" in out
    assert "no_secrets" in out
    assert "Scan complete" in out


def test_security_check_json_output(capsys):
    fake_report = {
        "status": "FAIL",
        "findings": [],
        "scanned_items": 2,
        "failed_items": 1,
    }
    with patch("security_platform.scanner.SecurityScanner") as cls:
        cls.return_value.scan.return_value = fake_report
        code = security_check(["--json"])
    assert code == 1
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "FAIL"
    assert data["failed_items"] == 1


def test_security_check_with_path_in_finding(capsys):
    fake_report = {
        "status": "FAIL",
        "findings": [
            {
                "name": "hardcoded_key",
                "passed": False,
                "severity": "critical",
                "details": "found key",
                "path": "secret.py",
            }
        ],
        "scanned_items": 1,
        "failed_items": 1,
    }
    with patch("security_platform.scanner.SecurityScanner") as cls:
        cls.return_value.scan.return_value = fake_report
        code = security_check([])
    assert code == 1
    out = capsys.readouterr().out
    assert "secret.py" in out
    assert "FAIL" in out


def test_main_routes_security_check():
    with patch("yasinai.cli.security_entrypoint.security_check", return_value=0) as sc:
        with pytest.raises(SystemExit) as exc:
            main(["security", "check"])
        assert exc.value.code == 0
        sc.assert_called_once_with([])


def test_main_routes_security_check_with_json_flag():
    with patch("yasinai.cli.security_entrypoint.security_check", return_value=0) as sc:
        with pytest.raises(SystemExit) as exc:
            main(["security", "check", "--json"])
        assert exc.value.code == 0
        sc.assert_called_once_with(["--json"])


def test_main_delegates_other_commands_to_cli():
    mock_cli = MagicMock()
    with patch("importlib.import_module", return_value=mock_cli) as imp:
        main(["status"])
        imp.assert_called_once_with("yasinai.cli.main")
        mock_cli.main.assert_called_once_with(["status"])
