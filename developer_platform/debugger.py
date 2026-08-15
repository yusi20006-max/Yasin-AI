"""
Debugging and Execution Tracer for YasinAI Developer Platform.
Tracks agent steps, inputs, outputs, and status.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Debugger:
    """
    Simulates a step-by-step developer debugger for tracing AI agent execution workflows.
    """

    def __init__(self) -> None:
        self.current_agent: str | None = None
        self.logs: list[dict[str, Any]] = []

    def start_session(self, agent_name: str) -> None:
        """
        Start a new debugging/tracing session for the given agent.
        """
        logger.info(f"Starting developer debugger tracing session for agent: '{agent_name}'")
        self.current_agent = agent_name
        self.logs = []

    def log_step(self, step_name: str, input_data: Any, output_data: Any) -> None:
        """
        Record an execution step inside the active session.
        """
        if not self.current_agent:
            logger.error("Failed to log step: No active debugging session.")
            raise RuntimeError("No active debugging session. Call start_session() first.")

        logger.debug(f"Debugging log step: '{step_name}' on agent '{self.current_agent}'")
        self.logs.append({
            "agent": self.current_agent,
            "step": step_name,
            "input": input_data,
            "output": output_data
        })

    def get_session_logs(self) -> list[dict[str, Any]]:
        """
        Retrieve all execution logs recorded in the current session.
        """
        return self.logs

    def clear_session(self) -> None:
        """
        Reset and clear the current debug session.
        """
        logger.info("Clearing active debugger session.")
        self.current_agent = None
        self.logs = []
