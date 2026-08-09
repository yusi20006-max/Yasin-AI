# YasinAI Developer SDK

The developer platform exposes a small stable plugin contract without forcing plugins to depend on runtime internals.

## Plugin

```python
from developer_platform import PluginRegistry, PluginSpec

registry = PluginRegistry()
registry.register(PluginSpec("echo", lambda value: value))
result = registry.invoke("echo", "hello")
```

Plugins have a name, semantic version, description, metadata, and callable handler. Registration is explicit and duplicate names are rejected.

The `@plugin(...)` decorator is available when metadata should travel with a handler before it is registered. It does not mutate global state or implicitly register code.

This API is intentionally synchronous and in-process for Phase 9. Sandboxing, permissions, remote plugins, and lifecycle management belong to later platform layers.
