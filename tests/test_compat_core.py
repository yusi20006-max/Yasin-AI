"""#132 — Yasin-Core compatibility against Public API Contract v1."""
from __future__ import annotations

from yasinai.core.config import Config
from yasinai.core.runtime import Runtime


def test_core_runtime_lifecycle():
    rt = Runtime(config_defaults={"modules": []})
    rt.start()
    assert rt.state == Runtime.READY
    info = rt.system_info.get_info()
    assert "version" in info or info.get("status")
    rt.shutdown()
    assert rt.state == Runtime.STOPPED


def test_core_config_public_api():
    cfg = Config(defaults={"app_name": "YasinAI", "debug": False})
    assert cfg.get("app_name") == "YasinAI"
    assert cfg.get("debug") is False


def test_core_does_not_require_private_platforms():
    # Importing Runtime must not require consumers to import private packages
    import yasinai.core.runtime as runtime_mod

    src = open(runtime_mod.__file__, encoding="utf-8").read()
    assert "knowledge_platform" not in src
    assert "developer_platform" not in src
