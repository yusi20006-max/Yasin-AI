"""Plugin SDK for YasinAI."""

from typing import Dict, Any, Optional, Type


class PluginMetadata:
    """Represents metadata configuration for a plugin."""

    def __init__(self, name: str, version: str, description: str = "") -> None:
        self.name = name
        self.version = version
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        """Convert plugin metadata to a dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }


class BasePlugin:
    """Base Plugin class for external extensions."""

    def __init__(self, metadata: PluginMetadata) -> None:
        self.metadata = metadata
        self.status = "CREATED"

    def initialize(self) -> None:
        """Lifecycle hook: Called when the plugin is loaded and initialized."""
        self.status = "INITIALIZED"

    def shutdown(self) -> None:
        """Lifecycle hook: Called when the plugin is unloaded/shut down."""
        self.status = "SHUTDOWN"


class PluginLoader:
    """Simple plugin loader interface to manage plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, BasePlugin] = {}

    def load_plugin(self, plugin: BasePlugin) -> None:
        """Load and initialize a plugin."""
        plugin.initialize()
        self._plugins[plugin.metadata.name] = plugin

    def unload_plugin(self, name: str) -> Optional[BasePlugin]:
        """Shut down and unload a plugin."""
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.shutdown()
        return plugin

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Retrieve a loaded plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> Dict[str, Dict[str, str]]:
        """List all currently loaded plugins."""
        return {name: plugin.metadata.to_dict() for name, plugin in self._plugins.items()}
