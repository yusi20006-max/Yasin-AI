"""Unit tests for the YasinAI Core Runtime."""

import os
import tempfile
import pytest
from yasinai.core.config import load_config, Configuration
from yasinai.core.system import SystemRegistry, SystemInfo
from yasinai.core.bootstrap import BootstrapManager
from yasinai.core.runtime import RuntimeOrchestrator


def test_configuration_loading():
    # Test loading from environment variables
    os.environ["YASINAI_PORT"] = "8080"
    os.environ["YASINAI_DEBUG"] = "true"

    config = load_config()
    assert config.get("port") == "8080"
    assert config.get("debug") == "true"

    # Test loading from temporary config file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".conf", encoding="utf-8") as temp_file:
        temp_file.write("env=production\n")
        temp_file.write("# comment line\n")
        temp_file.write("db_host = localhost\n")
        temp_filepath = temp_file.name

    try:
        config_with_file = load_config(temp_filepath)
        assert config_with_file.get("env") == "production"
        assert config_with_file.get("db_host") == "localhost"
        assert config_with_file.get("port") == "8080"  # Environment still applies
    finally:
        os.unlink(temp_filepath)
        del os.environ["YASINAI_PORT"]
        del os.environ["YASINAI_DEBUG"]


def test_system_info_and_registry():
    sys_info = SystemInfo()
    assert sys_info.version == "1.0.0"
    assert isinstance(sys_info.python_version, str)
    assert isinstance(sys_info.platform, str)

    registry = SystemRegistry()
    registry.register("test_service", "service_instance")
    assert registry.get("test_service") == "service_instance"
    assert "test_service" in registry.list_services()

    registry.unregister("test_service")
    assert registry.get("test_service") is None
    assert "test_service" not in registry.list_services()


def test_bootstrap_manager():
    registry = SystemRegistry()
    manager = BootstrapManager(registry)

    # Mock module
    class MockModule:
        @staticmethod
        def register_service(reg):
            reg.register("mock_service", "mocked")

    import sys
    sys.modules["mock_bootstrap_module"] = MockModule

    module = manager.load_module("mock_bootstrap_module")
    assert module is MockModule
    assert registry.get("mock_service") == "mocked"
    assert "mock_bootstrap_module" in manager.loaded_modules


def test_runtime_orchestrator():
    orchestrator = RuntimeOrchestrator()
    assert orchestrator.state == "STOPPED"

    # Validate registered core services
    assert orchestrator.registry.get("config") is not None
    assert orchestrator.registry.get("system_info") is not None

    orchestrator.startup()
    assert orchestrator.state == "READY"

    orchestrator.shutdown()
    assert orchestrator.state == "STOPPED"
    assert orchestrator.registry.get("config") is None
