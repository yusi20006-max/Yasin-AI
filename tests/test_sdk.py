"""Tests for developer_platform.sdk (PluginRegistry, PluginSpec, decorator)."""
from __future__ import annotations

import pytest

from developer_platform.sdk import (
    PluginError,
    PluginRegistry,
    PluginSpec,
    SDKError,
    plugin,
)


def test_plugin_spec_defaults():
    spec = PluginSpec(name="echo", handler=lambda x: x)
    assert spec.name == "echo"
    assert spec.version == "1.0.0"
    assert spec.description == ""
    assert spec.metadata == {}


def test_registry_register_list_invoke():
    registry = PluginRegistry()
    assert list(registry.list()) == []

    def echo(msg: str) -> str:
        return msg

    spec = PluginSpec(name="echo", handler=echo, version="1.1.0", description="Echo")
    registered = registry.register(spec)
    assert registered is spec
    assert [p.name for p in registry.list()] == ["echo"]
    assert registry.get("echo") is spec
    assert registry.invoke("echo", "ok") == "ok"


def test_registry_rejects_empty_name():
    registry = PluginRegistry()
    with pytest.raises(PluginError, match="empty"):
        registry.register(PluginSpec(name="  ", handler=lambda: None))
    with pytest.raises(PluginError, match="empty"):
        registry.register(PluginSpec(name="", handler=lambda: None))


def test_registry_rejects_duplicates_and_missing():
    registry = PluginRegistry()
    registry.register(PluginSpec("echo", lambda: None))
    with pytest.raises(PluginError, match="already registered"):
        registry.register(PluginSpec("echo", lambda: None))
    with pytest.raises(PluginError, match="not found"):
        registry.invoke("missing")


def test_registry_unregister():
    registry = PluginRegistry()
    registry.register(PluginSpec("tmp", lambda: 1))
    assert registry.unregister("tmp") is True
    assert registry.get("tmp") is None
    assert registry.unregister("tmp") is False


def test_decorator_attaches_metadata():
    @plugin("calculator", version="2.0.0", description="add", metadata={"op": "add"})
    def calculate(a: int, b: int) -> int:
        return a + b

    assert calculate(2, 3) == 5
    spec = calculate.__yasinai_plugin__
    assert isinstance(spec, PluginSpec)
    assert spec.name == "calculator"
    assert spec.version == "2.0.0"
    assert spec.description == "add"
    assert spec.metadata == {"op": "add"}
    assert spec.handler is calculate


def test_sdk_error_hierarchy():
    assert issubclass(PluginError, SDKError)
    assert issubclass(SDKError, Exception)
