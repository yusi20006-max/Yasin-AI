"""Plugin SDK for Developer Platform."""

from typing import Dict, Any, Optional, List


class Plugin:
    """Base class for building platform/agent plugins."""

    def __init__(self, name: str, version: str = "1.0.0", description: Optional[str] = None):
        """Initializes the plugin with metadata.

        Args:
            name: The plugin's unique name.
            version: Version string.
            description: Summary of plugin capabilities.
        """
        self.name = name
        self.version = version
        self.description = description or ""
        self.is_loaded = False

    def on_load(self) -> None:
        """Lifecycle hook called when the plugin is loaded."""
        self.is_loaded = True

    def on_unload(self) -> None:
        """Lifecycle hook called when the plugin is unloaded."""
        self.is_loaded = False

    def execute_action(self, action_name: str, *args, **kwargs) -> Any:
        """Executes a registered action on the plugin.

        Args:
            action_name: Name of the action to execute.
        """
        if not self.is_loaded:
            raise RuntimeError(f"Plugin '{self.name}' must be loaded before executing actions.")

        # Dispatch dynamically if method exists
        method = getattr(self, action_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        raise AttributeError(f"Plugin '{self.name}' has no action '{action_name}'.")

    def to_dict(self) -> Dict[str, Any]:
        """Returns plugin metadata as a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "loaded": self.is_loaded
        }


class PluginLoader:
    """Manager to load, track, and manage custom plugins."""

    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}

    def load_plugin(self, plugin: Plugin) -> None:
        """Loads and registers a plugin.

        Args:
            plugin: Plugin instance.
        """
        plugin.on_load()
        self._plugins[plugin.name] = plugin

    def unload_plugin(self, name: str) -> bool:
        """Unloads a registered plugin by name.

        Args:
            name: Name of the plugin.

        Returns:
            True if plugin was found and unloaded, False otherwise.
        """
        if name in self._plugins:
            self._plugins[name].on_unload()
            del self._plugins[name]
            return True
        return False

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Retrieves a registered plugin."""
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """Lists metadata of all registered plugins."""
        return [p.to_dict() for p in self._plugins.values()]
