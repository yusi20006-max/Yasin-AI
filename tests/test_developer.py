"""Tests for YasinAI Developer Platform."""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
import pytest

from yasinai.developer_platform.agent_sdk import AgentMetadata, BaseAgent, AgentRegistry
from yasinai.developer_platform.plugin_sdk import PluginMetadata, BasePlugin, PluginLoader
from yasinai.developer_platform.application_sdk import ApplicationConfig, Application
from yasinai.developer_platform.generator import ScaffoldGenerator
from yasinai.developer_platform.package_builder import PackageBuilder
from yasinai.cli.main import main


# 1. Agent SDK Tests
def test_agent_sdk():
    metadata = AgentMetadata(name="TestAgent", version="1.2.3", description="A test agent", author="Tester")
    assert metadata.name == "TestAgent"
    assert metadata.version == "1.2.3"
    assert metadata.to_dict()["author"] == "Tester"

    class CustomAgent(BaseAgent):
        def execute(self, task: str, **kwargs):
            return f"Executed: {task}"

    agent = CustomAgent(metadata)
    assert agent.status == "CREATED"

    agent.initialize()
    assert agent.status == "INITIALIZED"

    result = agent.execute("run query")
    assert result == "Executed: run query"

    agent.shutdown()
    assert agent.status == "SHUTDOWN"

    registry = AgentRegistry()
    registry.register(agent)
    assert registry.get_agent("TestAgent") == agent
    assert "TestAgent" in registry.list_agents()


# 2. Plugin SDK Tests
def test_plugin_sdk():
    metadata = PluginMetadata(name="TestPlugin", version="0.1.0", description="A test plugin")
    assert metadata.name == "TestPlugin"
    assert metadata.version == "0.1.0"
    assert metadata.to_dict()["description"] == "A test plugin"

    class CustomPlugin(BasePlugin):
        pass

    plugin = CustomPlugin(metadata)
    assert plugin.status == "CREATED"

    loader = PluginLoader()
    loader.load_plugin(plugin)
    assert plugin.status == "INITIALIZED"
    assert loader.get_plugin("TestPlugin") == plugin
    assert "TestPlugin" in loader.list_plugins()

    loader.unload_plugin("TestPlugin")
    assert plugin.status == "SHUTDOWN"
    assert loader.get_plugin("TestPlugin") is None


# 3. Application SDK Tests
def test_application_sdk():
    config = ApplicationConfig(app_name="TestApp", version="1.0.0", settings={"debug": True})
    assert config.app_name == "TestApp"
    assert config.settings["debug"] is True

    app = Application(config)

    # Register Agent
    agent_meta = AgentMetadata(name="AppAgent", version="1.0.0")
    class AppAgent(BaseAgent):
        def execute(self, task: str, **kwargs):
            return "ok"
    agent = AppAgent(agent_meta)
    app.register_agent(agent)
    assert app.agent_registry.get_agent("AppAgent") == agent

    # Register Plugin
    plugin_meta = PluginMetadata(name="AppPlugin", version="1.0.0")
    plugin = BasePlugin(plugin_meta)
    app.register_plugin(plugin)
    assert app.plugin_loader.get_plugin("AppPlugin") == plugin

    # Register Custom Component
    app.register_custom_component("db", "SQLite")
    assert app.get_custom_component("db") == "SQLite"


# 4. Generator System Tests
def test_generator_system():
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_dir = ScaffoldGenerator.generate_agent_scaffold("My Cool Agent", target_dir=tmpdir)
        path = Path(agent_dir)

        assert path.exists()
        assert (path / "config.json").exists()
        assert (path / "src" / "agent.py").exists()
        assert (path / "tests" / "test_agent.py").exists()

        with open(path / "config.json") as f:
            content = f.read()
            assert "My Cool Agent" in content


# 5. Package Builder Tests
def test_package_builder():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Invalid package directory
        is_valid, errors = PackageBuilder.validate_package(tmpdir)
        assert is_valid is False
        assert len(errors) > 0

        # Correct scaffold
        agent_dir = ScaffoldGenerator.generate_agent_scaffold("Builder Agent", target_dir=tmpdir)
        is_valid, errors = PackageBuilder.validate_package(agent_dir)
        assert is_valid is True
        assert len(errors) == 0

        # Build package
        dist_dir = os.path.join(tmpdir, "dist")
        zip_path = PackageBuilder.build_package(agent_dir, output_dir=dist_dir)
        assert os.path.exists(zip_path)
        assert zip_path.endswith(".zip")

        # Verify Zip contents
        with zipfile.ZipFile(zip_path, "r") as zipf:
            namelist = zipf.namelist()
            assert "config.json" in namelist
            assert "src/agent.py" in namelist


# 6. CLI Integration Tests
def test_cli_integration(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        # We need to change the working directory or pass target path to test scaffold creation/building
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Test `yasin agent create`
            exit_code = main(["agent", "create", "CLI Agent"])
            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Successfully created agent scaffold" in captured.out
            assert os.path.exists("cli_agent_agent")

            # Test `yasin package build`
            exit_code = main(["package", "build", "cli_agent_agent"])
            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Successfully built package archive" in captured.out
            assert os.path.exists("dist")

            # Clean up the output directory if created
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            if os.path.exists("cli_agent_agent"):
                shutil.rmtree("cli_agent_agent")

        finally:
            os.chdir(orig_cwd)
