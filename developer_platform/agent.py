"""
Agent SDK for YasinAI Developer Platform.
Manages AI agent definitions, task execution, and agent lifecycle.
"""

from typing import Dict, List, Optional


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
        self.status = "active"

    def stop(self) -> None:
        """
        Transition the agent status to inactive.
        """
        self.status = "inactive"

    def execute_task(self, task: str) -> str:
        """
        Execute a given task. Returns execution result details.
        """
        if self.status != "active":
            raise RuntimeError(f"Agent '{self.name}' must be active to execute tasks.")

        # Simple task simulation
        result = f"Agent '{self.name}' (Role: {self.role}) successfully completed task: '{task}'"
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
            raise ValueError(f"Agent '{name}' already exists.")

        agent = Agent(name, role, description, type)
        self._agents[name] = agent
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
            return True
        return False

    def list_agents(self) -> List[Agent]:
        """
        List all registered agents.
        """
        return list(self._agents.values())
