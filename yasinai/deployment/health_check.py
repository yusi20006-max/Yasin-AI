"""
Health Check System for YasinAI Deployment.
Verifies post-deployment integrity of Core Runtime, CLI, Security Platform, and Knowledge Platform.
"""

import argparse
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class HealthCheck:
    """
    Performs comprehensive health checks across all integrated platforms.
    """

    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run verification on all platforms and return detailed status.
        """
        logger.info("Running health checks on all platforms...")
        checks: Dict[str, Dict[str, Any]] = {
            "runtime": self.check_runtime(),
            "cli": self.check_cli(),
            "security_platform": self.check_security_platform(),
            "knowledge_platform": self.check_knowledge_platform(),
        }

        overall_success: bool = all(v["success"] for v in checks.values())
        status: str = "HEALTHY" if overall_success else "DEGRADED"
        logger.info(f"Health checks completed. Status: {status}")

        return {
            "success": overall_success,
            "status": status,
            "platforms": checks
        }

    def check_runtime(self) -> Dict[str, Any]:
        """
        Verify that the Core Runtime can boot and return status.
        """
        logger.debug("Checking Core Runtime health...")
        try:
            from yasinai.core.runtime import Runtime
            runtime = Runtime()
            runtime.start()
            info = runtime.system_info.get_info()
            runtime.shutdown()

            logger.debug("Core Runtime health check: OK")
            return {
                "success": True,
                "message": "Core Runtime loaded and booted successfully.",
                "details": info
            }
        except Exception as e:
            logger.error(f"Core Runtime health check: FAILED: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Core Runtime verification failed: {str(e)}",
                "details": {}
            }

    def check_cli(self) -> Dict[str, Any]:
        """
        Verify that the CLI interface is configured and responsive.
        """
        logger.debug("Checking CLI health...")
        try:
            from yasinai.cli.main import create_parser
            parser = create_parser()
            subcommands = []
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice in action.choices:
                        subcommands.append(choice)

            success = len(subcommands) > 0
            logger.debug(f"CLI health check: {'OK' if success else 'FAILED'}")
            return {
                "success": success,
                "message": "CLI parser instantiated successfully." if success else "CLI parser has no subcommands registered.",
                "subcommands_found": subcommands
            }
        except Exception as e:
            logger.error(f"CLI health check: FAILED: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"CLI verification failed: {str(e)}",
                "subcommands_found": []
            }

    def check_security_platform(self) -> Dict[str, Any]:
        """
        Verify that Security Platform components are functional.
        """
        logger.debug("Checking Security Platform health...")
        try:
            from security_platform.identity import IdentityManager
            from security_platform.encryption import EncryptionEngine

            id_mgr = IdentityManager()
            # Roles need to be created before assigning them
            id_mgr.create_role("admin", "Administrator role")
            user = id_mgr.create_user(username="health_check_user", roles=["admin"])

            enc_engine = EncryptionEngine()
            key = enc_engine.generate_key()
            enc_data = enc_engine.encrypt("health_check_secret", key)
            dec_data = enc_engine.decrypt(enc_data, key)

            success = user is not None and dec_data == "health_check_secret"
            logger.debug(f"Security Platform health check: {'OK' if success else 'FAILED'}")
            return {
                "success": success,
                "message": "Security Platform identity and encryption validated." if success else "Identity or encryption mismatch.",
                "identity_ok": user is not None,
                "encryption_ok": dec_data == "health_check_secret"
            }
        except Exception as e:
            logger.error(f"Security Platform health check: FAILED: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Security Platform verification failed: {str(e)}",
                "identity_ok": False,
                "encryption_ok": False
            }

    def check_knowledge_platform(self) -> Dict[str, Any]:
        """
        Verify that Knowledge Platform memory and search components are functional.
        """
        logger.debug("Checking Knowledge Platform health...")
        try:
            from knowledge_platform.memory import MemoryManager
            from knowledge_platform.semantic_search import Retriever

            mem_mgr = MemoryManager()
            mem_mgr.add_short_term("Health check message.", {"session": "hc_session"})
            short_mem = mem_mgr.get_short_term()

            retriever = Retriever()
            retriever.add_document("hc_doc", "YasinAI deployment verification document.")
            results = retriever.retrieve("deployment", limit=1)

            success = len(short_mem) > 0 and len(results) > 0
            logger.debug(f"Knowledge Platform health check: {'OK' if success else 'FAILED'}")
            return {
                "success": success,
                "message": "Knowledge Platform memory storage and retrieval validated." if success else "Memory storage or retrieval failed.",
                "memory_ok": len(short_mem) > 0,
                "search_ok": len(results) > 0
            }
        except Exception as e:
            logger.error(f"Knowledge Platform health check: FAILED: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Knowledge Platform verification failed: {str(e)}",
                "memory_ok": False,
                "search_ok": False
            }
