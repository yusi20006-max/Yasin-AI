"""Application SDK for Developer Platform."""

from typing import Dict, Any, Optional, List
from yasinai.developer_platform.agent_sdk import Agent
from yasinai.developer_platform.plugin_sdk import Plugin


class Application:
    """Represents a unified AI application container structure."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initializes the Application container.

        Args:
            name: Human-readable application name.
            config: Key-value options for application behavior.
        """
        self.name = name
        self.config = config or {}
        self.agents: Dict[str, Agent] = {}
        self.plugins: Dict[str, Plugin] = {}
        self.components: Dict[str, Any] = {}
        self.is_running = False

    def configure(self, key: str, value: Any) -> None:
        """Sets an application configuration value."""
        self.config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration option."""
        return self.config.get(key, default)

    def register_agent(self, agent: Agent) -> None:
        """Registers an AI agent to the application."""
        self.agents[agent.name] = agent

    def register_plugin(self, plugin: Plugin) -> None:
        """Registers and loads a plugin to the application."""
        plugin.on_load()
        self.plugins[plugin.name] = plugin

    def register_component(self, name: str, component: Any) -> None:
        """Registers any generic module or custom service."""
        self.components[name] = component

    def start(self) -> None:
        """Starts the application container."""
        self.is_running = True
        # Propagate starts if objects support them
        for agent in self.agents.values():
            agent.on_start()

    def stop(self) -> None:
        """Stops the application container."""
        for agent in self.agents.values():
            agent.on_stop()
        for plugin in self.plugins.values():
            plugin.on_unload()
        self.is_running = False

    def to_dict(self) -> Dict[str, Any]:
        """Provides container structural overview."""
        return {
            "name": self.name,
            "config": self.config,
            "agents": list(self.agents.keys()),
            "plugins": list(self.plugins.keys()),
            "components": list(self.components.keys()),
            "is_running": self.is_running
        }
