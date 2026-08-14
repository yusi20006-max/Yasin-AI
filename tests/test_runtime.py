import json
from unittest.mock import MagicMock, patch

import pytest

from yasinai.core.bootstrap import Bootstrap
from yasinai.core.config import Config
from yasinai.core.runtime import Runtime
from yasinai.core.system import ServiceRegistry, SystemInfo


def test_config_defaults():
    config = Config()
    assert config.get("app_name") == "YasinAI"
    assert config.get("version") == "1.1.0"
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
    config_data = {"app_name": "FileYasin", "debug": True, "modules": ["mod1", "mod2"]}
    config_file.write_text(json.dumps(config_data))
    config = Config()
    assert config.load_from_file(str(config_file)) is True
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
    registry.register_service("test_service", mock_service)
    assert registry.has_service("test_service") is True
    assert registry.get_service("test_service") == mock_service
    with pytest.raises(ValueError):
        registry.register_service("test_service", "new_service")
    registry.register_service("test_service", "new_service", overwrite=True)
    assert registry.get_service("test_service") == "new_service"
    services = registry.list_services()
    assert services["test_service"] == "new_service"
    assert registry.unregister_service("test_service") is True
    assert registry.has_service("test_service") is False
    assert registry.unregister_service("test_service") is False
    with pytest.raises(KeyError):
        registry.get_service("test_service")


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
    assert bootstrap.loaded_modules == ["mock_mod"]


def test_bootstrap_skips_duplicate_modules():
    runtime = MagicMock()
    bootstrap = Bootstrap(runtime)
    mock_module = MagicMock()
    mock_module.register_module = MagicMock()
    with patch("importlib.import_module", return_value=mock_module) as mock_import:
        assert bootstrap.discover_and_load(["mock_mod", "mock_mod"]) == ["mock_mod"]
    mock_import.assert_called_once_with("mock_mod")
    mock_module.register_module.assert_called_once_with(runtime)


def test_bootstrap_rejects_non_callable_registration_hook():
    runtime = MagicMock()
    bootstrap = Bootstrap(runtime)
    mock_module = MagicMock()
    mock_module.register_module = "invalid"
    with patch("importlib.import_module", return_value=mock_module):
        with pytest.raises(ImportError, match="register_module is not callable"):
            bootstrap.discover_and_load(["mock_mod"])


def test_bootstrap_load_failure():
    runtime = MagicMock()
    bootstrap = Bootstrap(runtime)
    with patch("importlib.import_module", side_effect=ImportError("Module not found")):
        with pytest.raises(ImportError, match="invalid_mod"):
            bootstrap.discover_and_load(["invalid_mod"])


def test_runtime_lifecycle():
    runtime = Runtime(config_defaults={"modules": []})
    assert runtime.state == Runtime.STOPPED
    assert runtime.system_info.status == "inactive"
    runtime.startup()
    assert runtime.state == Runtime.STARTING
    assert runtime.system_info.status == "starting"
    assert runtime.services.has_service("config") is True
    assert runtime.services.has_service("system_info") is True
    runtime.bootstrap()
    assert runtime.state == Runtime.BOOTSTRAPPING
    runtime.initialize()
    assert runtime.state == Runtime.INITIALIZING
    runtime.register_modules()
    assert runtime.state == Runtime.REGISTERING_MODULES
    runtime.ready()
    assert runtime.state == Runtime.READY
    assert runtime.system_info.status == "ready"
    assert runtime.services.has_service("runtime") is True
    runtime.shutdown()
    assert runtime.state == Runtime.STOPPED
    assert runtime.system_info.status == "shutdown"
    assert runtime.services.list_services() == {}


def test_runtime_invalid_lifecycle_transition():
    runtime = Runtime()
    with pytest.raises(RuntimeError):
        runtime.bootstrap()
    runtime.startup()
    with pytest.raises(RuntimeError):
        runtime.ready()


def test_runtime_orchestrated_start_is_idempotent():
    runtime = Runtime(config_defaults={"modules": []})
    runtime.start()
    assert runtime.state == Runtime.READY
    runtime.start()
    assert runtime.state == Runtime.READY
    runtime.shutdown()
    runtime.shutdown()
    assert runtime.state == Runtime.STOPPED


def test_runtime_start_failure_cleans_up():
    runtime = Runtime(config_defaults={"modules": ["invalid_mod"]})
    with patch("importlib.import_module", side_effect=ImportError("Module not found")):
        with pytest.raises(RuntimeError, match="Runtime startup failed"):
            runtime.start()
    assert runtime.state == Runtime.FAILED
    assert runtime.system_info.status == "failed"
    assert runtime.services.list_services() == {}
    assert runtime.last_error is not None


def test_runtime_start_cannot_continue_from_partial_manual_state():
    runtime = Runtime()
    runtime.startup()
    with pytest.raises(RuntimeError, match="Cannot start from state: STARTING"):
        runtime.start()
    runtime.shutdown()
    assert runtime.state == Runtime.STOPPED


def test_additional_runtime_coverage(tmp_path, monkeypatch):
    config = Config()
    assert config.load_from_file("nonexistent.json") is False
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid")
    assert config.load_from_file(str(invalid_file)) is False
    list_file = tmp_path / "list.json"
    list_file.write_text("[1, 2, 3]")
    assert config.load_from_file(str(list_file)) is False

    config = Config(defaults={"some_int": 10, "some_float": 1.5, "some_bool": False, "some_list": ["a"]})
    monkeypatch.setenv("YASINAI_SOME_INT", "abc")
    monkeypatch.setenv("YASINAI_SOME_FLOAT", "xyz")
    monkeypatch.setenv("YASINAI_SOME_LIST", "[abc]")
    config._load_from_env()
    assert config.get("some_int") == 10
    assert config.get("some_float") == 1.5
    assert config.get("some_list") == ["a"]
    monkeypatch.setenv("YASINAI_SOME_LIST", "[\"x\", \"y\"]")
    config._load_from_env()
    assert config.get("some_list") == ["x", "y"]
    config.set("dynamic_key", "dynamic_val")
    assert config.get("dynamic_key") == "dynamic_val"
    assert config.get("nonexistent_key", "fallback") == "fallback"
    assert config.to_dict()["dynamic_key"] == "dynamic_val"

    runtime = Runtime()
    with pytest.raises(RuntimeError):
        runtime.initialize()
    with pytest.raises(RuntimeError):
        runtime.register_modules()
    with pytest.raises(RuntimeError):
        runtime.ready()

    sys_info = SystemInfo()
    with patch("platform.platform", side_effect=Exception("platform error")):
        info = sys_info.get_info()
        assert info["platform"] == "Unknown"
        assert info["os"] == "Unknown"
        assert info["architecture"] == "Unknown"
