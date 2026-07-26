"""
Plugin SDK for YasinAI Developer Platform.
Manages external extensions and third-party modules.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Plugin:
    """
    Represents a third-party plugin or system extension.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "An external plugin extension",
        enabled: bool = True,
    ) -> None:
        self.name: str = name
        self.version: str = version
        self.description: str = description
        self.enabled: bool = enabled
        self.is_initialized: bool = False

    def initialize(self) -> None:
        """
        Initialize the plugin's environment or dependencies.
        """
        logger.info(f"Initializing plugin: '{self.name}' (v{self.version})")
        self.is_initialized = True

    def execute(self, action: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute an extension action supported by the plugin.
        """
        logger.debug(f"Executing action '{action}' on plugin '{self.name}' with args={args}, kwargs={kwargs}")
        if not self.enabled:
            logger.error(f"Cannot execute plugin action: Plugin '{self.name}' is disabled.")
            raise RuntimeError(f"Plugin '{self.name}' is disabled and cannot execute actions.")
        if not self.is_initialized:
            logger.error(f"Cannot execute plugin action: Plugin '{self.name}' is not initialized.")
            raise RuntimeError(f"Plugin '{self.name}' is not initialized.")

        # Simple simulated plugin action execution
        result = f"Plugin '{self.name}' successfully executed action '{action}' with arguments: {args}, {kwargs}"
        logger.info(f"Plugin '{self.name}' successfully executed action '{action}'")
        return result

    def __repr__(self) -> str:
        return f"Plugin(name={self.name!r}, version={self.version!r}, enabled={self.enabled})"


class PluginSDK:
    """
    Plugin SDK Manager responsible for registering and controlling third-party modules.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a new plugin with the SDK.
        """
        if plugin.name in self._plugins:
            logger.error(f"Cannot register plugin: '{plugin.name}' is already registered.")
            raise ValueError(f"Plugin '{plugin.name}' is already registered.")
        self._plugins[plugin.name] = plugin
        logger.info(f"Successfully registered plugin: '{plugin.name}'")

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Look up a registered plugin by name.
        """
        return self._plugins.get(name)

    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin by name.
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = True
            logger.info(f"Enabled plugin: '{name}'")
            return True
        logger.warning(f"Failed to enable plugin: '{name}' not found.")
        return False

    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin by name.
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = False
            logger.info(f"Disabled plugin: '{name}'")
            return True
        logger.warning(f"Failed to disable plugin: '{name}' not found.")
        return False

    def list_plugins(self) -> List[Plugin]:
        """
        List all registered plugins.
        """
        return list(self._plugins.values())
