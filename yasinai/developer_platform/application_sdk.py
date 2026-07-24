"""Application SDK for YasinAI."""

from typing import Dict, Any, Optional
from yasinai.developer_platform.agent_sdk import BaseAgent, AgentRegistry
from yasinai.developer_platform.plugin_sdk import BasePlugin, PluginLoader


class ApplicationConfig:
    """Represents application configuration settings."""

    def __init__(self, app_name: str, version: str = "1.0.0", settings: Optional[Dict[str, Any]] = None) -> None:
        self.app_name = app_name
        self.version = version
        self.settings = settings or {}


class Application:
    """Represents a YasinAI developer application."""

    def __init__(self, config: ApplicationConfig) -> None:
        self.config = config
        self.agent_registry = AgentRegistry()
        self.plugin_loader = PluginLoader()
        self.components: Dict[str, Any] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent into the application agent registry."""
        agent.initialize()
        self.agent_registry.register(agent)

    def register_plugin(self, plugin: BasePlugin) -> None:
        """Load and register a plugin into the application plugin loader."""
        self.plugin_loader.load_plugin(plugin)

    def register_custom_component(self, name: str, component: Any) -> None:
        """Register a generic custom component to the application context."""
        self.components[name] = component

    def get_custom_component(self, name: str) -> Optional[Any]:
        """Retrieve a custom component from the application context."""
        return self.components.get(name)
