"""SDK contract tests kept close to the developer platform."""

from .sdk import PluginError, PluginRegistry, PluginSpec, plugin


def test_registry_register_list_and_invoke():
    registry = PluginRegistry()
    spec = PluginSpec("echo", lambda value: value, description="Echo")
    registry.register(spec)
    assert [item.name for item in registry.list()] == ["echo"]
    assert registry.invoke("echo", "ok") == "ok"


def test_registry_rejects_duplicates_and_missing_plugins():
    registry = PluginRegistry()
    registry.register(PluginSpec("echo", lambda: None))
    try:
        registry.register(PluginSpec("echo", lambda: None))
        assert False
    except PluginError:
        pass
    try:
        registry.invoke("missing")
        assert False
    except PluginError:
        pass


def test_decorator_exposes_metadata_without_global_registration():
    @plugin("calculator", version="2.0.0", description="calculator")
    def calculate(a, b):
        return a + b

    assert calculate(2, 3) == 5
    spec = calculate.__yasinai_plugin__
    assert spec.name == "calculator"
    assert spec.version == "2.0.0"
