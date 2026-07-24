"""Agent SDK for Developer Platform."""

from typing import Dict, Any, Optional, List


class Agent:
    """Base class for building custom agents."""

    def __init__(self, name: str, version: str = "1.0.0", description: Optional[str] = None):
        """Initializes the base Agent with metadata.

        Args:
            name: Human-readable agent name.
            version: Version string.
            description: Optional summary of agent capabilities.
        """
        self.name = name
        self.version = version
        self.description = description or ""
        self.state = "uninitialized"
        self.on_init()

    def on_init(self) -> None:
        """Lifecycle hook called upon agent instantiation."""
        self.state = "initialized"

    def on_start(self) -> None:
        """Lifecycle hook called when the agent starts execution."""
        self.state = "running"

    def on_stop(self) -> None:
        """Lifecycle hook called when the agent stops execution."""
        self.state = "stopped"

    def execute(self, task: str) -> Dict[str, Any]:
        """Executes a simple task interface.

        Args:
            task: Task string description.

        Returns:
            Result dictionary from task execution.
        """
        self.on_start()
        result = {
            "agent": self.name,
            "version": self.version,
            "task": task,
            "status": "success",
            "output": f"Executed task '{task}' successfully."
        }
        self.on_stop()
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Returns agent metadata as a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "state": self.state
        }


class AgentRegistry:
    """Registry to manage and support agent registration."""

    def __init__(self):
        self._agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Registers an agent instance.

        Args:
            agent: Custom agent instance.
        """
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """Retrieves an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """Lists registered agents with metadata."""
        return [agent.to_dict() for agent in self._agents.values()]
