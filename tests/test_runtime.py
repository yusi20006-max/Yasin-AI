import json
from unittest.mock import MagicMock, patch
import pytest
from yasinai.core.config import Config
from yasinai.core.system import SystemInfo, ServiceRegistry
from yasinai.core.bootstrap import Bootstrap
from yasinai.core.runtime import Runtime


# 1. Tests for Config Loading
def test_config_defaults():
    config = Config()
    assert config.get("app_name") == "YasinAI"
    assert config.get("version") == "1.0.0"
    assert config.get("debug") is False
    assert config.get("modules") == []


def test_config_custom_defaults():
    custom = {"app_name": "CustomYasin", "debug": True, "custom_key": 42}
    config = Config(defaults=custom)
    assert config.get("app_name") == "CustomYasin"
    assert config.get("debug") is True
    assert config.get("custom_key") == 42


def test_config_load_from_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_data = {
        "app_name": "FileYasin",
        "debug": True,
        "modules": ["mod1", "mod2"]
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    config = Config()
    success = config.load_from_file(str(config_file))
    assert success is True
    assert config.get("app_name") == "FileYasin"
    assert config.get("debug") is True
    assert config.get("modules") == ["mod1", "mod2"]


def test_config_env_overrides(monkeypatch):
    monkeypatch.setenv("YASINAI_APP_NAME", "EnvYasin")
    monkeypatch.setenv("YASINAI_DEBUG", "True")
    monkeypatch.setenv("YASINAI_MODULES", "mod_env1,mod_env2")

    config = Config()
    assert config.get("app_name") == "EnvYasin"
    assert config.get("debug") is True
    assert config.get("modules") == ["mod_env1", "mod_env2"]


# 2. Tests for System and Service Registry
def test_system_info():
    sys_info = SystemInfo(app_name="TestSystem", version="2.0.0", status="active")
    info = sys_info.get_info()
    assert info["app_name"] == "TestSystem"
    assert info["version"] == "2.0.0"
    assert info["status"] == "active"
    assert "python_version" in info
    assert "platform" in info


def test_service_registry():
    registry = ServiceRegistry()
    mock_service = MagicMock()

    # Registration
    registry.register_service("test_service", mock_service)
    assert registry.has_service("test_service") is True
    assert registry.get_service("test_service") == mock_service

    # Prevent duplicate registration without overwrite
    with pytest.raises(ValueError):
        registry.register_service("test_service", "new_service")

    # Overwrite
    registry.register_service("test_service", "new_service", overwrite=True)
    assert registry.get_service("test_service") == "new_service"

    # Listing
    services = registry.list_services()
    assert "test_service" in services
    assert services["test_service"] == "new_service"

    # Unregister
    assert registry.unregister_service("test_service") is True
    assert registry.has_service("test_service") is False
    assert registry.unregister_service("test_service") is False
    with pytest.raises(KeyError):
        registry.get_service("test_service")


# 3. Tests for Bootstrap Module Discovery and Loading
def test_bootstrap_load():
    runtime = MagicMock()
    bootstrap = Bootstrap(runtime)

    mock_module = MagicMock()
    mock_register = MagicMock()
    mock_module.register_module = mock_register

    with patch("importlib.import_module", return_value=mock_module) as mock_import:
        loaded = bootstrap.discover_and_load(["mock_mod"])
        assert loaded == ["mock_mod"]
        mock_import.assert_called_once_with("mock_mod")
        mock_register.assert_called_once_with(runtime)
        assert "mock_mod" in bootstrap.loaded_modules


def test_bootstrap_load_failure():
    runtime = MagicMock()
    bootstrap = Bootstrap(runtime)

    with patch("importlib.import_module", side_effect=ImportError("Module not found")):
        with pytest.raises(ImportError):
            bootstrap.discover_and_load(["invalid_mod"])


# 4. Tests for Runtime Lifecycle flow
def test_runtime_lifecycle():
    runtime = Runtime(config_defaults={"modules": []})
    assert runtime.state == "STOPPED"
    assert runtime.system_info.status == "inactive"

    # 1. Startup
    runtime.startup()
    assert runtime.state == "STARTING"
    assert runtime.system_info.status == "starting"
    assert runtime.services.has_service("config") is True
    assert runtime.services.has_service("system_info") is True

    # 2. Bootstrap
    runtime.bootstrap()
    assert runtime.state == "BOOTSTRAPPING"

    # 3. Initialize
    runtime.initialize()
    assert runtime.state == "INITIALIZING"

    # 4. Register Modules
    runtime.register_modules()
    assert runtime.state == "REGISTERING_MODULES"

    # 5. Ready
    runtime.ready()
    assert runtime.state == "READY"
    assert runtime.system_info.status == "ready"
    assert runtime.services.has_service("runtime") is True

    # 6. Shutdown
    runtime.shutdown()
    assert runtime.state == "STOPPED"
    assert runtime.system_info.status == "shutdown"
    # All services should have been unregistered
    assert len(runtime.services.list_services()) == 0


def test_runtime_invalid_lifecycle_transition():
    runtime = Runtime()
    # Cannot bootstrap directly from STOPPED
    with pytest.raises(RuntimeError):
        runtime.bootstrap()

    runtime.startup()
    # Cannot ready directly from STARTING
    with pytest.raises(RuntimeError):
        runtime.ready()


def test_runtime_orchestrated_start():
    # Test high-level start method
    runtime = Runtime(config_defaults={"modules": []})
    runtime.start()
    assert runtime.state == "READY"
    assert runtime.system_info.status == "ready"
