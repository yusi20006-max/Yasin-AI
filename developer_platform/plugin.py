"""
Plugin SDK for YasinAI Developer Platform.
Manages external extensions and third-party modules.
"""
from __future__ import annotations

import logging
from typing import Any

from developer_platform.sdk import PluginTrustError

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
        trusted: bool = True,
    ) -> None:
        self.name: str = name
        self.version: str = version
        self.description: str = description
        self.enabled: bool = enabled
        self.is_initialized: bool = False
        self.trusted: bool = trusted

    def initialize(self) -> None:
        """
        Initialize the plugin's environment or dependencies.
        """
        logger.info(f"Initializing plugin: '{self.name}' (v{self.version})")
        self.is_initialized = True

    def execute(self, action: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute an extension action supported by the plugin.

        Note: this is a simulated/reference implementation — it returns a
        descriptive string and does not perform real sandboxed execution of
        plugin code. Real execution is out of scope for this in-process SDK.
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

    def __init__(self, *, allow_untrusted: bool = False) -> None:
        self._plugins: dict[str, Plugin] = {}
        self.allow_untrusted = allow_untrusted

    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a new plugin with the SDK.

        Production policy requires ``plugin.trusted`` to be True unless this
        SDK instance was explicitly constructed with ``allow_untrusted=True``.
        This mirrors the trust policy enforced by
        ``developer_platform.sdk.PluginRegistry`` so there is a single,
        consistent trust boundary regardless of which plugin API is used.
        """
        if plugin.name in self._plugins:
            logger.error(f"Cannot register plugin: '{plugin.name}' is already registered.")
            raise ValueError(f"Plugin '{plugin.name}' is already registered.")
        if not plugin.trusted and not self.allow_untrusted:
            logger.error(
                f"Refusing untrusted plugin '{plugin.name}': in-process plugins must be "
                "trusted code; construct PluginSDK(allow_untrusted=True) only for isolated "
                "non-production use."
            )
            raise PluginTrustError(
                f"refusing untrusted plugin '{plugin.name}': in-process plugins must be "
                "trusted code; set allow_untrusted=True only for isolated non-production use"
            )
        self._plugins[plugin.name] = plugin
        logger.info(f"Successfully registered plugin: '{plugin.name}'")

    def get_plugin(self, name: str) -> Plugin | None:
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

    def list_plugins(self) -> list[Plugin]:
        """
        List all registered plugins.
        """
        return list(self._plugins.values())
