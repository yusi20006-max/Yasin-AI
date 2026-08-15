"""
Profiler and Performance Analytics for YasinAI Developer Platform.
Measures execution times and resource utilization metrics.
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class Profiler:
    """
    Helps developers profile their agents, plugins, and app execution paths.
    """

    def __init__(self) -> None:
        self.start_times: dict[str, float] = {}
        self.profiles: dict[str, float] = {}

    def start_profile(self, operation_name: str) -> None:
        """
        Record the start timestamp for a specific operation.
        """
        logger.debug(f"Starting profiling for operation: '{operation_name}'")
        self.start_times[operation_name] = time.time()

    def end_profile(self, operation_name: str) -> float:
        """
        Record the end timestamp, calculate elapsed time, and save profile metrics.
        """
        if operation_name not in self.start_times:
            logger.error(f"Failed to end profile: No active profiling found for '{operation_name}'.")
            raise ValueError(f"No active profiling found for '{operation_name}'.")

        elapsed: float = time.time() - self.start_times[operation_name]
        self.profiles[operation_name] = elapsed
        del self.start_times[operation_name]
        logger.info(f"Operation '{operation_name}' profiled in {elapsed:.6f} seconds.")
        return elapsed

    def get_profile_report(self) -> dict[str, Any]:
        """
        Generate a performance report of all profiled operations.
        """
        logger.debug("Generating profile report...")
        if not self.profiles:
            return {"status": "no profiles recorded"}

        total_time: float = sum(self.profiles.values())
        avg_time: float = total_time / len(self.profiles)

        return {
            "total_operations": len(self.profiles),
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "breakdown": self.profiles.copy()
        }

    def clear_profiles(self) -> None:
        """
        Reset all recorded profiles and timings.
        """
        logger.info("Clearing all recorded profiles.")
        self.start_times.clear()
        self.profiles.clear()
