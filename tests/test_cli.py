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
    assert "serve" in choices


# Test 'serve' subcommand parser options
def test_serve_parser_options():
    parser = create_parser()
    args = parser.parse_args(["serve", "--interval", "10", "--json"])
    assert args.command == "serve"
    assert args.interval == 10
    assert args.json is True


def test_handle_serve_invalid_interval(capsys):
    from yasinai.cli.main import handle_serve
    args = argparse.Namespace(interval=0, json=False)
    exit_code = handle_serve(args)
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Interval must be a positive integer." in captured.err


@patch("time.sleep")
@patch("yasinai.deployment.health_check.HealthCheck.run_all_checks")
def test_serve_command_loop(mock_run_all, mock_sleep, capsys):
    import os
    import signal
    from yasinai.cli.main import handle_serve
    mock_run_all.return_value = {"success": True, "status": "HEALTHY"}
    args = argparse.Namespace(interval=5, json=False)

    # Simulate SIGINT signal inside time.sleep
    def sleep_side_effect(secs):
        os.kill(os.getpid(), signal.SIGINT)

    mock_sleep.side_effect = sleep_side_effect

    exit_code = handle_serve(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "YasinAI Foreground Serve" in captured.out
    assert "YasinAI Core Runtime started in foreground supervisor mode" in captured.out
    assert "Health Check Status: HEALTHY" in captured.out
    assert "Shutting down YasinAI Core Runtime cleanly..." in captured.out


@patch("time.sleep")
@patch("yasinai.deployment.health_check.HealthCheck.run_all_checks")
def test_serve_command_json_output(mock_run_all, mock_sleep, capsys):
    import os
    import signal
    from yasinai.cli.main import handle_serve
    mock_run_all.return_value = {"success": True, "status": "HEALTHY"}
    args = argparse.Namespace(interval=1, json=True)

    # Simulate SIGTERM signal inside time.sleep
    def sleep_side_effect(secs):
        os.kill(os.getpid(), signal.SIGTERM)

    mock_sleep.side_effect = sleep_side_effect

    exit_code = handle_serve(args)
    assert exit_code == 0
    captured = capsys.readouterr()

    lines = [json.loads(line) for line in captured.out.strip().split("\n")]
    assert len(lines) >= 3
    assert lines[0]["event"] == "startup"
    assert lines[0]["status"] == "running"
    assert lines[1]["event"] == "health_check"
    assert lines[1]["status"] == "HEALTHY"
    assert lines[1]["success"] is True
    assert lines[-1]["event"] == "shutdown"
    assert lines[-1]["status"] == "stopped"


@patch("time.sleep")
@patch("yasinai.deployment.health_check.HealthCheck.run_all_checks")
def test_serve_command_graceful_shutdown(mock_run_all, mock_sleep, capsys):
    import os
    import signal
    from yasinai.cli.main import handle_serve
    mock_run_all.return_value = {"success": False, "status": "DEGRADED"}
    args = argparse.Namespace(interval=5, json=False)

    def sleep_side_effect(secs):
        os.kill(os.getpid(), signal.SIGINT)

    mock_sleep.side_effect = sleep_side_effect

    exit_code = handle_serve(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Health Check Status: DEGRADED" in captured.out
    assert "Shutting down YasinAI Core Runtime cleanly..." in captured.out


def test_handle_serve_exception_path(capsys):
    from yasinai.cli.main import handle_serve
    args = argparse.Namespace(interval=5, json=False)
    with patch("yasinai.cli.main.Runtime") as mock_runtime_class:
        mock_instance = MagicMock()
        mock_instance.start.side_effect = Exception("Runtime startup failure")
        mock_runtime_class.return_value = mock_instance

        exit_code = handle_serve(args)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error in serve loop: Runtime startup failure" in captured.err


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
def test_handle_package_build_text(capsys, tmp_path):
    output_dir = str(tmp_path / "custom_dist") + "/"
    args = argparse.Namespace(
        output=output_dir,
        version="2.1.0",
        json=False
    )
    exit_code = handle_package_build(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Building YasinAI deployment package v2.1.0..." in captured.out
    assert f"Target directory: {output_dir}" in captured.out
    assert f"SUCCESS: Created build artifact: {output_dir}yasinai-pkg-2.1.0.tar.gz" in captured.out


def test_handle_package_build_json(capsys, tmp_path):
    output_dir = str(tmp_path / "custom_dist") + "/"
    args = argparse.Namespace(
        output=output_dir,
        version="2.1.0",
        json=True
    )
    exit_code = handle_package_build(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["success"] is True
    assert data["package_name"] == "yasinai-pkg-2.1.0.tar.gz"
    assert data["output_directory"] == output_dir


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


def test_main_package_build(capsys, tmp_path):
    output_dir = str(tmp_path / "build") + "/"
    with pytest.raises(SystemExit) as exc_info:
        main(["package", "build", "--output", output_dir])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Building YasinAI deployment package" in captured.out


def test_additional_cli_coverage(capsys):
    # 1. handle_agent_create exception path (lines 89-92)
    with patch("developer_platform.agent.AgentSDK.create_agent", side_effect=Exception("Agent creation failed")):
        args = argparse.Namespace(name="agent", role="general", description="desc", type="std", json=False)
        assert handle_agent_create(args) == 1
        captured = capsys.readouterr()
        assert "Error creating agent: Agent creation failed" in captured.err

    # 2. handle_memory_search empty results path (line 142) and exception path (lines 148-151)
    args_empty = argparse.Namespace(query="nonexistent_word", limit=5, threshold=0.99, json=False)
    assert handle_memory_search(args_empty) == 0
    captured = capsys.readouterr()
    assert "No matching memories found." in captured.out

    with patch(
        "yasinai.integration.cli_client.YasinCLIClient.search_memory",
        side_effect=Exception("Memory search failed"),
    ):
        args = argparse.Namespace(query="test", limit=5, threshold=0.7, json=False)
        assert handle_memory_search(args) == 1
        captured = capsys.readouterr()
        assert "Error searching memory: Memory search failed" in captured.err

    # 3. handle_security_check exception path (lines 195-198)
    # Raising exception by mocking json.dumps when json output is enabled
    with patch("json.dumps", side_effect=Exception("JSON dump failed")):
        args = argparse.Namespace(json=True)
        assert handle_security_check(args) == 1
        captured = capsys.readouterr()
        assert "Error checking security: JSON dump failed" in captured.err

    # 4. handle_package_build exception path (lines 231-234)
    with patch("developer_platform.package_builder.PackageBuilder.build_package", side_effect=Exception("Package build failed")):
        args = argparse.Namespace(output="dist/", version="1.0.0", json=False)
        assert handle_package_build(args) == 1
        captured = capsys.readouterr()
        assert "Error building package: Package build failed" in captured.err

    # 5. main --json options logic (lines 329-330)
    with patch("yasinai.cli.main.hasattr") as mock_hasattr:
        # We mock hasattr to return False specifically for "json", but True otherwise
        mock_hasattr.side_effect = lambda obj, name: False if name == "json" else (True if name == "func" else hasattr(obj, name))
        with pytest.raises(SystemExit) as exc_info:
            main(["status", "--json"])
        assert exc_info.value.code == 0

    # 6. main choice subcommand parser missing choice (lines 324-325)
    # We mock subcommand choices get to return None
    class CustomDict(dict):
        def get(self, key, default=None):
            return None

    modified_parser = create_parser()
    for action in modified_parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            custom_choices = CustomDict(action.choices)
            action.choices = custom_choices
    with patch("yasinai.cli.main.create_parser", return_value=modified_parser):
        with pytest.raises(SystemExit) as exc_info:
            main(["agent"])
        assert exc_info.value.code == 0

    # 7. main when args has no func attribute (lines 334-335)
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(command="status", json=False)):
        with pytest.raises(SystemExit) as exc_info:
            main(["status"])
        assert exc_info.value.code == 0

    # 8. Run as main script via subprocess to execute lines 302 and 339
    import subprocess
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    res = subprocess.run([sys.executable, "yasinai/cli/main.py", "--help"], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "YasinAI Command Line management interface" in res.stdout

    # Run module main
    res_mod = subprocess.run([sys.executable, "-m", "yasinai.cli", "--help"], capture_output=True, text=True, env=env)
    assert res_mod.returncode == 0

    # 9. Call main(None) to execute line 302 in current process
    with patch("sys.argv", ["yasin", "status"]):
        with pytest.raises(SystemExit) as exc_info:
            main(None)
        assert exc_info.value.code == 0
