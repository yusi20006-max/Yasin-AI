"""Generator System for YasinAI."""

import os
from pathlib import Path


class ScaffoldGenerator:
    """Generates project/app/agent scaffolds with templates."""

    @staticmethod
    def generate_agent_scaffold(name: str, target_dir: str = ".") -> str:
        """Create a standard agent scaffold in the target directory."""
        # Clean up agent name for directory/file name
        clean_name = name.lower().replace(" ", "_").replace("-", "_")
        agent_dir = Path(target_dir) / f"{clean_name}_agent"
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (agent_dir / "src").mkdir(parents=True, exist_ok=True)
        (agent_dir / "tests").mkdir(parents=True, exist_ok=True)

        # Create files
        # __init__.py
        with open(agent_dir / "src" / "__init__.py", "w") as f:
            f.write(f'# {name} Agent Source\n')

        # agent.py
        agent_code = f"""\"\"\"{name} Agent implementation.\"\"\"

from yasinai.developer_platform.agent_sdk import BaseAgent, AgentMetadata


class {clean_name.title().replace("_", "")}Agent(BaseAgent):
    \"\"\"Custom agent implementation.\"\"\"

    def __init__(self) -> None:
        metadata = AgentMetadata(
            name="{name}",
            version="1.0.0",
            description="Scaffolded {name} Agent",
            author="Developer"
        )
        super().__init__(metadata)

    def execute(self, task: str, **kwargs):
        \"\"\"Execute tasks.\"\"\"
        return f"Executing task '{{task}}' with agent {name}"
"""
        with open(agent_dir / "src" / "agent.py", "w") as f:
            f.write(agent_code)

        # config.json
        config_json = f"""{{
  "name": "{name}",
  "version": "1.0.0",
  "description": "Scaffolded {name} Agent",
  "entrypoint": "src.agent.{clean_name.title().replace("_", "")}Agent"
}}
"""
        with open(agent_dir / "config.json", "w") as f:
            f.write(config_json)

        # test_agent.py
        test_code = f"""\"\"\"Tests for {name} Agent.\"\"\"

from src.agent import {clean_name.title().replace("_", "")}Agent


def test_agent_execution():
    agent = {clean_name.title().replace("_", "")}Agent()
    agent.initialize()
    result = agent.execute("test task")
    assert "test task" in result
"""
        with open(agent_dir / "tests" / "test_agent.py", "w") as f:
            f.write(test_code)

        return str(agent_dir)
