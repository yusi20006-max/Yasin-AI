"""Unit and integration tests for YasinAI Developer Platform."""

import os
import shutil
import pytest
from unittest.mock import patch

from yasinai.developer_platform.agent_sdk import Agent, AgentRegistry
from yasinai.developer_platform.plugin_sdk import Plugin, PluginLoader
from yasinai.developer_platform.application_sdk import Application
from yasinai.developer_platform.generator import ProjectGenerator
from yasinai.developer_platform.package_builder import PackageBuilder
from yasinai.cli.main import main


# Cleanup fixture
@pytest.fixture
def temp_dirs():
    dirs = ["tests/temp_scaffold", "dist"]
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
    yield dirs
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)


def test_agent_sdk():
    agent = Agent(name="TestAgent", version="1.2.0", description="A test agent.")
    assert agent.name == "TestAgent"
    assert agent.version == "1.2.0"
    assert agent.description == "A test agent."
    assert agent.state == "initialized"

    res = agent.execute("run math")
    assert res["status"] == "success"
    assert "run math" in res["output"]
    assert agent.state == "stopped"

    registry = AgentRegistry()
    assert len(registry.list_agents()) == 0

    registry.register(agent)
    assert len(registry.list_agents()) == 1
    assert registry.get_agent("TestAgent") == agent


def test_plugin_sdk():
    plugin = Plugin(name="TestPlugin", version="2.0.0", description="A test plugin.")
    assert plugin.name == "TestPlugin"
    assert plugin.is_loaded is False

    loader = PluginLoader()
    loader.load_plugin(plugin)
    assert plugin.is_loaded is True
    assert loader.get_plugin("TestPlugin") == plugin

    # Mock action execution
    with pytest.raises(AttributeError):
        plugin.execute_action("non_existent")

    class CustomPlugin(Plugin):
        def my_action(self, val):
            return val * 2

    cp = CustomPlugin("CP")
    loader.load_plugin(cp)
    assert cp.execute_action("my_action", 5) == 10

    assert loader.unload_plugin("CP") is True
    assert cp.is_loaded is False


def test_application_sdk():
    app = Application("MyAIApp")
    assert app.name == "MyAIApp"
    assert app.is_running is False

    agent = Agent("AppAgent")
    plugin = Plugin("AppPlugin")

    app.register_agent(agent)
    app.register_plugin(plugin)
    app.register_component("custom_db", {"host": "localhost"})

    assert "AppAgent" in app.to_dict()["agents"]
    assert "AppPlugin" in app.to_dict()["plugins"]
    assert "custom_db" in app.to_dict()["components"]

    app.start()
    assert app.is_running is True
    assert agent.state == "running"

    app.stop()
    assert app.is_running is False
    assert agent.state == "stopped"
    assert plugin.is_loaded is False


def test_generator_system(temp_dirs):
    output_parent = "tests/temp_scaffold"
    success = ProjectGenerator.generate_agent_scaffold(output_parent, "Pegasus")
    assert success is True

    agent_dir = os.path.join(output_parent, "pegasus")
    assert os.path.exists(agent_dir)
    assert os.path.exists(os.path.join(agent_dir, "config.json"))
    assert os.path.exists(os.path.join(agent_dir, "agent.py"))
    assert os.path.exists(os.path.join(agent_dir, "README.md"))
    assert os.path.exists(os.path.join(agent_dir, "__init__.py"))


def test_package_builder(temp_dirs):
    output_parent = "tests/temp_scaffold"
    ProjectGenerator.generate_agent_scaffold(output_parent, "Pegasus")
    agent_dir = os.path.join(output_parent, "pegasus")

    # Validate correct scaffold
    errors = PackageBuilder.validate_package(agent_dir)
    assert len(errors) == 0

    # Build package
    output_dir = "dist"
    archive = PackageBuilder.build_package(agent_dir, output_dir)
    assert archive is not None
    assert os.path.exists(archive)
    assert archive.endswith(".zip")


def test_cli_integration(temp_dirs):
    with patch("sys.stdout") as mock_stdout:
        # 1. Test 'yasin agent create'
        exit_code_create = main(["agent", "create", "Orion"])
        assert exit_code_create == 0

        # Verify Orion scaffold directory exists
        orion_dir = "./orion"
        assert os.path.exists(orion_dir)

        try:
            # 2. Test 'yasin package build' on Orion scaffold
            exit_code_build = main(["package", "build", orion_dir])
            assert exit_code_build == 0

            # Check build dist exists
            assert os.path.exists("dist")
            zip_files = [f for f in os.listdir("dist") if f.startswith("orion") and f.endswith(".zip")]
            assert len(zip_files) > 0
        finally:
            # Cleanup generated orion folder
            if os.path.exists(orion_dir):
                shutil.rmtree(orion_dir)
