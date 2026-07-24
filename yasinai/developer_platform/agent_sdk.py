"""Agent SDK for YasinAI."""

from typing import Dict, Any, Optional, Type


class AgentMetadata:
    """Represents the metadata configuration of an agent."""

    def __init__(self, name: str, version: str, description: str = "", author: str = "") -> None:
        self.name = name
        self.version = version
        self.description = description
        self.author = author

    def to_dict(self) -> Dict[str, str]:
        """Convert metadata to a dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
        }


class BaseAgent:
    """Base Agent class that defines the core agent interface and lifecycle hooks."""

    def __init__(self, metadata: AgentMetadata) -> None:
        self.metadata = metadata
        self.status = "CREATED"

    def initialize(self) -> None:
        """Lifecycle hook: Called during agent initialization."""
        self.status = "INITIALIZED"

    def execute(self, task: str, **kwargs) -> Any:
        """Lifecycle hook: Main execution entry point for agent tasks."""
        raise NotImplementedError("Agents must implement the execute method.")

    def shutdown(self) -> None:
        """Lifecycle hook: Called during agent shutdown."""
        self.status = "SHUTDOWN"


class AgentRegistry:
    """Registry to keep track of registered agents and their metadata."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent instance in the registry."""
        name = agent.metadata.name
        self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Retrieve a registered agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> Dict[str, Dict[str, str]]:
        """List all registered agents and their metadata."""
        return {name: agent.metadata.to_dict() for name, agent in self._agents.items()}
