"""
Debugging and Execution Tracer for YasinAI Developer Platform.
Tracks agent steps, inputs, outputs, and status.
"""

from typing import Any, Dict, List, Optional


class Debugger:
    """
    Simulates a step-by-step developer debugger for tracing AI agent execution workflows.
    """

    def __init__(self) -> None:
        self.current_agent: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []

    def start_session(self, agent_name: str) -> None:
        """
        Start a new debugging/tracing session for the given agent.
        """
        self.current_agent = agent_name
        self.logs = []

    def log_step(self, step_name: str, input_data: Any, output_data: Any) -> None:
        """
        Record an execution step inside the active session.
        """
        if not self.current_agent:
            raise RuntimeError("No active debugging session. Call start_session() first.")

        self.logs.append({
            "agent": self.current_agent,
            "step": step_name,
            "input": input_data,
            "output": output_data
        })

    def get_session_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieve all execution logs recorded in the current session.
        """
        return self.logs

    def clear_session(self) -> None:
        """
        Reset and clear the current debug session.
        """
        self.current_agent = None
        self.logs = []
