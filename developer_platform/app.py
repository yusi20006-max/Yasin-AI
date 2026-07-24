"""
Application SDK for YasinAI Developer Platform.
Provides building blocks for creating AI-powered applications.
"""

from typing import Any, Dict, List, Optional
from developer_platform.agent import Agent
from developer_platform.plugin import Plugin


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
            raise ValueError(f"Agent '{agent.name}' already added to this application.")
        self._agents[agent.name] = agent

    def add_plugin(self, plugin: Plugin) -> None:
        """
        Add a plugin to the application.
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' already added to this application.")
        self._plugins[plugin.name] = plugin

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
        steps_executed = []
        result_payload = {}

        # Simulating workflow execution:
        # 1. Initialize and execute plugins if any
        for name, plugin in self._plugins.items():
            if not plugin.is_initialized:
                plugin.initialize()
            plugin_res = plugin.execute("process_input", query=input_query)
            steps_executed.append(f"Plugin '{name}' processing")
            result_payload[f"plugin_{name}"] = plugin_res

        # 2. Run agents to answer query
        agent_responses = []
        for name, agent in self._agents.items():
            if agent.status != "active":
                agent.start()
            res = agent.execute_task(input_query)
            steps_executed.append(f"Agent '{name}' executing")
            agent_responses.append(res)
            result_payload[f"agent_{name}"] = res

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
            raise ValueError(f"AI Application '{name}' already exists.")
        app = AIApplication(name, config)
        self._applications[name] = app
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
            return True
        return False

    def list_applications(self) -> List[AIApplication]:
        """
        List all registered AI Applications.
        """
        return list(self._applications.values())
