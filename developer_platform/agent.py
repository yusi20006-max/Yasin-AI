"""
Agent SDK for YasinAI Developer Platform.
Manages AI agent definitions, task execution, and agent lifecycle.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Agent:
    """
    Represents an AI Agent with associated roles, configuration, and state.
    """

    def __init__(
        self,
        name: str,
        role: str = "general",
        description: str = "A helpful AI agent",
        type: str = "standard",
        status: str = "inactive",
    ) -> None:
        self.name: str = name
        self.role: str = role
        self.description: str = description
        self.type: str = type
        self.status: str = status

    def start(self) -> None:
        """
        Transition the agent status to active.
        """
        logger.info(f"Starting agent: '{self.name}'")
        self.status = "active"

    def stop(self) -> None:
        """
        Transition the agent status to inactive.
        """
        logger.info(f"Stopping agent: '{self.name}'")
        self.status = "inactive"

    def execute_task(self, task: str) -> str:
        """
        Execute a given task. Returns execution result details.
        """
        logger.debug(f"Agent '{self.name}' requested to execute task: '{task}'")
        if self.status != "active":
            logger.error(f"Cannot execute task: Agent '{self.name}' is inactive.")
            raise RuntimeError(f"Agent '{self.name}' must be active to execute tasks.")

        # Simple task simulation
        result = f"Agent '{self.name}' (Role: {self.role}) successfully completed task: '{task}'"
        logger.info(f"Agent '{self.name}' successfully completed task.")
        return result

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, role={self.role!r}, type={self.type!r}, status={self.status!r})"


class AgentSDK:
    """
    Agent SDK Manager responsible for the creation, lifecycle, and management of agents.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    def create_agent(
        self,
        name: str,
        role: str = "general",
        description: str = "A helpful AI agent",
        type: str = "standard",
    ) -> Agent:
        """
        Create and register a new AI Agent.
        """
        if name in self._agents:
            logger.error(f"Cannot create agent: '{name}' already exists.")
            raise ValueError(f"Agent '{name}' already exists.")

        agent = Agent(name, role, description, type)
        self._agents[name] = agent
        logger.info(f"Successfully registered agent: '{name}'")
        return agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Retrieve an agent by name.
        """
        return self._agents.get(name)

    def delete_agent(self, name: str) -> bool:
        """
        Delete a registered agent. Returns True if deleted.
        """
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Successfully deleted agent registration: '{name}'")
            return True
        logger.warning(f"Attempted to delete non-existent agent: '{name}'")
        return False

    def list_agents(self) -> List[Agent]:
        """
        List all registered agents.
        """
        return list(self._agents.values())
