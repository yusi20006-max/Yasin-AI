"""
Application SDK for YasinAI Developer Platform.
Provides building blocks for creating AI-powered applications.
"""

import logging
from typing import Any, Dict, List, Optional
from developer_platform.agent import Agent
from developer_platform.plugin import Plugin
from developer_platform.sdk import PluginTrustError

logger = logging.getLogger(__name__)


class AIApplication:
    """
    Represents an end-to-end AI Application composed of agents and plugins.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.name: str = name
        self.config: Dict[str, Any] = config or {}
        self._agents: Dict[str, Agent] = {}
        self._plugins: Dict[str, Plugin] = {}

    def add_agent(self, agent: Agent) -> None:
        """
        Add an AI agent to the application.
        """
        if agent.name in self._agents:
            logger.error(f"Cannot add agent '{agent.name}': already added to application '{self.name}'.")
            raise ValueError(f"Agent '{agent.name}' already added to this application.")
        self._agents[agent.name] = agent
        logger.info(f"Agent '{agent.name}' added to application '{self.name}'.")

    def add_plugin(self, plugin: Plugin, *, allow_untrusted: bool = False) -> None:
        """
        Add a plugin to the application.

        Enforces the same production trust policy as
        ``developer_platform.plugin.PluginSDK.register_plugin`` — untrusted
        plugins are rejected unless ``allow_untrusted=True`` is explicitly
        passed, so this entry point cannot bypass the trust boundary.
        """
        if plugin.name in self._plugins:
            logger.error(f"Cannot add plugin '{plugin.name}': already added to application '{self.name}'.")
            raise ValueError(f"Plugin '{plugin.name}' already added to this application.")
        if not plugin.trusted and not allow_untrusted:
            logger.error(
                f"Refusing untrusted plugin '{plugin.name}' for application '{self.name}': "
                "in-process plugins must be trusted code."
            )
            raise PluginTrustError(
                f"refusing untrusted plugin '{plugin.name}': in-process plugins must be "
                "trusted code; pass allow_untrusted=True only for isolated non-production use"
            )
        self._plugins[plugin.name] = plugin
        logger.info(f"Plugin '{plugin.name}' added to application '{self.name}'.")

    def list_agents(self) -> List[Agent]:
        """
        List all agents assigned to the application.
        """
        return list(self._agents.values())

    def list_plugins(self) -> List[Plugin]:
        """
        List all plugins assigned to the application.
        """
        return list(self._plugins.values())

    def run(self, input_query: str) -> Dict[str, Any]:
        """
        Run the application pipeline, invoking agents and plugins to answer the input query.
        """
        logger.info(f"Running AI Application '{self.name}' with query: '{input_query}'")
        steps_executed: List[str] = []
        result_payload: Dict[str, Any] = {}

        # Simulating workflow execution:
        # 1. Initialize and execute plugins if any
        for name, plugin in self._plugins.items():
            if not plugin.is_initialized:
                plugin.initialize()
            plugin_res = plugin.execute("process_input", query=input_query)
            steps_executed.append(f"Plugin '{name}' processing")
            result_payload[f"plugin_{name}"] = plugin_res

        # 2. Run agents to answer query
        agent_responses: List[str] = []
        for name, agent in self._agents.items():
            if agent.status != "active":
                agent.start()
            res = agent.execute_task(input_query)
            steps_executed.append(f"Agent '{name}' executing")
            agent_responses.append(res)
            result_payload[f"agent_{name}"] = res

        logger.info(f"AI Application '{self.name}' pipeline run completed successfully.")
        return {
            "application": self.name,
            "query": input_query,
            "status": "completed",
            "steps": steps_executed,
            "agent_responses": agent_responses,
            "payload": result_payload
        }

    def __repr__(self) -> str:
        return f"AIApplication(name={self.name!r}, agents={list(self._agents.keys())}, plugins={list(self._plugins.keys())})"


class AppSDK:
    """
    App SDK Manager responsible for orchestrating AI Applications.
    """

    def __init__(self) -> None:
        self._applications: Dict[str, AIApplication] = {}

    def create_application(self, name: str, config: Optional[Dict[str, Any]] = None) -> AIApplication:
        """
        Create and register a new AI Application.
        """
        if name in self._applications:
            logger.error(f"Cannot create application: '{name}' already exists.")
            raise ValueError(f"AI Application '{name}' already exists.")
        app = AIApplication(name, config)
        self._applications[name] = app
        logger.info(f"Successfully registered AI Application: '{name}'")
        return app

    def get_application(self, name: str) -> Optional[AIApplication]:
        """
        Get a registered AI Application.
        """
        return self._applications.get(name)

    def delete_application(self, name: str) -> bool:
        """
        Delete a registered AI Application.
        """
        if name in self._applications:
            del self._applications[name]
            logger.info(f"Successfully deleted AI Application: '{name}'")
            return True
        logger.warning(f"Attempted to delete non-existent AI Application: '{name}'")
        return False

    def list_applications(self) -> List[AIApplication]:
        """
        List all registered AI Applications.
        """
        return list(self._applications.values())
