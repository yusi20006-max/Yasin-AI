"""Deployment and runtime health check reporting system."""

import sys
from typing import Dict, Any, List


class HealthCheck:
    """Verifies the integration, importability, and status of all registered YasinAI platforms."""

    @staticmethod
    def run_all() -> Dict[str, Any]:
        """Runs import and readiness checks for all platforms.

        Returns:
            A health check execution report.
        """
        report: Dict[str, Any] = {
            "status": "HEALTHY",
            "platforms": {},
            "python_version": sys.version.split()[0],
            "issues": []
        }

        # 1. Core Runtime check
        try:
            from yasinai.core.runtime import RuntimeOrchestrator
            orch = RuntimeOrchestrator()
            report["platforms"]["core_runtime"] = {
                "available": True,
                "version": orch.system_info.version,
                "state": orch.state
            }
        except Exception as e:
            report["platforms"]["core_runtime"] = {"available": False, "error": str(e)}
            report["issues"].append(f"Core Runtime unavailable: {e}")

        # 2. Security Platform check
        # Since Security Platform may or may not be fully implemented yet, we try to import it
        try:
            # Try to see if security modules exist
            import security_platform
            report["platforms"]["security_platform"] = {"available": True, "status": "integrated"}
        except ImportError:
            # Or if it lives under yasinai.security_platform
            try:
                from yasinai import security_platform
                report["platforms"]["security_platform"] = {"available": True, "status": "integrated"}
            except ImportError:
                report["platforms"]["security_platform"] = {"available": False, "status": "missing"}
                report["issues"].append("Security Platform integration modules could not be imported.")

        # 3. Knowledge Platform check
        try:
            from yasinai.knowledge_platform.manager import MemoryManager
            from yasinai.knowledge_platform.graph import KnowledgeGraph
            report["platforms"]["knowledge_platform"] = {"available": True, "status": "fully_integrated"}
        except Exception as e:
            report["platforms"]["knowledge_platform"] = {"available": False, "error": str(e)}
            report["issues"].append(f"Knowledge Platform failed verification: {e}")

        # 4. Developer Platform check
        try:
            from yasinai.developer_platform.agent_sdk import Agent
            from yasinai.developer_platform.plugin_sdk import Plugin
            report["platforms"]["developer_platform"] = {"available": True, "status": "fully_integrated"}
        except Exception as e:
            report["platforms"]["developer_platform"] = {"available": False, "error": str(e)}
            report["issues"].append(f"Developer Platform failed verification: {e}")

        # 5. Final Status Calculation
        if report["issues"]:
            # If core runtime or essential parts are failing, set status to DEGRADED or UNHEALTHY
            core_ok = report["platforms"].get("core_runtime", {}).get("available", False)
            if not core_ok:
                report["status"] = "UNHEALTHY"
            else:
                report["status"] = "DEGRADED"

        return report
