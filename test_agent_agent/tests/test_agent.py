"""Tests for test-agent Agent."""

from src.agent import TestAgentAgent


def test_agent_execution():
    agent = TestAgentAgent()
    agent.initialize()
    result = agent.execute("test task")
    assert "test task" in result
