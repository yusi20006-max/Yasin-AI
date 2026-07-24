"""test-agent Agent implementation."""

from yasinai.developer_platform.agent_sdk import BaseAgent, AgentMetadata


class TestAgentAgent(BaseAgent):
    """Custom agent implementation."""

    def __init__(self) -> None:
        metadata = AgentMetadata(
            name="test-agent",
            version="1.0.0",
            description="Scaffolded test-agent Agent",
            author="Developer"
        )
        super().__init__(metadata)

    def execute(self, task: str, **kwargs):
        """Execute tasks."""
        return f"Executing task '{task}' with agent test-agent"
