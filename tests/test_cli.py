"""Unit tests for the YasinAI CLI System."""

import pytest
from yasinai.cli.main import main


def test_cli_status(capsys):
    exit_code = main(["status"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "YasinAI System Status:" in captured.out
    assert "Core State: STOPPED" in captured.out or "Core State: READY" in captured.out
    assert "Version: 1.0.0" in captured.out


def test_cli_agent_create(capsys):
    exit_code = main(["agent", "create", "test-agent"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Creating agent 'test-agent'..." in captured.out


def test_cli_memory_search(capsys):
    exit_code = main(["memory", "search", "cognitive function"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Searching memory for 'cognitive function'..." in captured.out


def test_cli_security_check(capsys):
    exit_code = main(["security", "check"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Running security check..." in captured.out


def test_cli_package_build(capsys):
    # With explicit path
    exit_code = main(["package", "build", "/tmp/project"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Building package at '/tmp/project'..." in captured.out

    # With default path (current directory)
    exit_code_default = main(["package", "build"])
    assert exit_code_default == 0
    captured_default = capsys.readouterr()
    assert "Building package at '.'..." in captured_default.out


def test_cli_unknown_command(capsys):
    # Testing unknown subcommands or invalid options
    with pytest.raises(SystemExit):
        main(["invalid_command"])
