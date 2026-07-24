import json
import sys
from unittest.mock import MagicMock, patch
import pytest
import argparse
from yasinai.cli.main import (
    create_parser,
    handle_status,
    handle_agent_create,
    handle_memory_search,
    handle_security_check,
    handle_package_build,
    main
)


# Test Parser creation and subparser configuration
def test_create_parser():
    parser = create_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "yasin"

    # Check that main subparsers exist
    actions = [action for action in parser._subparsers._actions if isinstance(action, argparse._SubParsersAction)]
    assert len(actions) > 0
    choices = actions[0].choices
    assert "status" in choices
    assert "agent" in choices
    assert "memory" in choices
    assert "security" in choices
    assert "package" in choices


# Test 'status' handler (text and JSON mode)
def test_handle_status_text(capsys):
    args = argparse.Namespace(json=False)
    exit_code = handle_status(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "YasinAI System Status" in captured.out
    assert "App Name:" in captured.out
    assert "Status:       ready" in captured.out


def test_handle_status_json(capsys):
    args = argparse.Namespace(json=True)
    exit_code = handle_status(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["app_name"] == "YasinAI"
    assert data["status"] == "ready"


def test_handle_status_exception(capsys):
    args = argparse.Namespace(json=False)
    # Mocking Runtime to raise exception on start
    with patch("yasinai.cli.main.Runtime") as mock_runtime_class:
        mock_instance = MagicMock()
        mock_instance.start.side_effect = Exception("Boot Failure")
        mock_runtime_class.return_value = mock_instance

        exit_code = handle_status(args)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error checking status: Boot Failure" in captured.err


# Test 'agent create' handler
def test_handle_agent_create_text(capsys):
    args = argparse.Namespace(
        name="test-agent",
        role="security",
        description="A secure agent",
        type="specialist",
        json=False
    )
    exit_code = handle_agent_create(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Creating agent 'test-agent'..." in captured.out
    assert "Role:        security" in captured.out
    assert "Description: A secure agent" in captured.out
    assert "Type:        specialist" in captured.out
    assert "SUCCESS: Agent 'test-agent' is ready to deploy." in captured.out


def test_handle_agent_create_json(capsys):
    args = argparse.Namespace(
        name="test-agent",
        role="security",
        description="A secure agent",
        type="specialist",
        json=True
    )
    exit_code = handle_agent_create(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["success"] is True
    assert data["agent"]["name"] == "test-agent"
    assert data["agent"]["role"] == "security"


# Test 'memory search' handler
def test_handle_memory_search_all_text(capsys):
    args = argparse.Namespace(
        query="",
        limit=5,
        threshold=0.7,
        json=False
    )
    exit_code = handle_memory_search(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Searching memory for query: '(all)'" in captured.out
    assert "Limit: 5 | Threshold: 0.7" in captured.out
    assert "YasinAI configuration loading rules." in captured.out


def test_handle_memory_search_filtered_json(capsys):
    args = argparse.Namespace(
        query="security",
        limit=2,
        threshold=0.8,
        json=True
    )
    exit_code = handle_memory_search(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["query"] == "security"
    assert len(data["results"]) == 1
    assert "Security platform and identity management" in data["results"][0]["content"]


# Test 'security check' handler
def test_handle_security_check_text(capsys):
    args = argparse.Namespace(json=False)
    exit_code = handle_security_check(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "YasinAI Security Platform - Audit Check" in captured.out
    assert "[ PASS ] Environment Secrets Check" in captured.out
    assert "Status: SECURE" in captured.out


def test_handle_security_check_json(capsys):
    args = argparse.Namespace(json=True)
    exit_code = handle_security_check(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "SECURE"
    assert data["failed_items"] == 0
    assert len(data["checks"]) == 4


# Test 'package build' handler
def test_handle_package_build_text(capsys):
    args = argparse.Namespace(
        output="custom_dist/",
        version="2.1.0",
        json=False
    )
    exit_code = handle_package_build(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Building YasinAI deployment package v2.1.0..." in captured.out
    assert "Target directory: custom_dist/" in captured.out
    assert "SUCCESS: Created build artifact: custom_dist/yasinai-pkg-2.1.0.tar.gz" in captured.out


def test_handle_package_build_json(capsys):
    args = argparse.Namespace(
        output="custom_dist/",
        version="2.1.0",
        json=True
    )
    exit_code = handle_package_build(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["success"] is True
    assert data["package_name"] == "yasinai-pkg-2.1.0.tar.gz"
    assert data["output_directory"] == "custom_dist/"


# Test main CLI dispatching and error/help handling
def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "YasinAI Command Line management interface" in captured.out


def test_main_no_args(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "YasinAI Command Line management interface" in captured.out


def test_main_subcommand_missing_choice(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["agent"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Create a new AI Agent" in captured.out


def test_main_status(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["status"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "YasinAI System Status" in captured.out


def test_main_agent_create(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["agent", "create", "cli-agent", "--role", "developer"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Creating agent 'cli-agent'..." in captured.out
    assert "Role:        developer" in captured.out


def test_main_memory_search(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["memory", "search", "config", "--limit", "1"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Searching memory for query: 'config'" in captured.out


def test_main_security_check(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["security", "check"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "YasinAI Security Platform - Audit Check" in captured.out


def test_main_package_build(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["package", "build", "--output", "build/"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Building YasinAI deployment package" in captured.out
