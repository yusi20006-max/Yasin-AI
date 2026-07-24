"""
Health Check System for YasinAI Deployment.
Verifies post-deployment integrity of Core Runtime, CLI, Security Platform, and Knowledge Platform.
"""

from typing import Any, Dict


class HealthCheck:
    """
    Performs comprehensive health checks across all integrated platforms.
    """

    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run verification on all platforms and return detailed status.
        """
        checks = {
            "runtime": self.check_runtime(),
            "cli": self.check_cli(),
            "security_platform": self.check_security_platform(),
            "knowledge_platform": self.check_knowledge_platform(),
        }

        overall_success = all(v["success"] for v in checks.values())

        return {
            "success": overall_success,
            "status": "HEALTHY" if overall_success else "DEGRADED",
            "platforms": checks
        }

    def check_runtime(self) -> Dict[str, Any]:
        """
        Verify that the Core Runtime can boot and return status.
        """
        try:
            from yasinai.core.runtime import Runtime
            runtime = Runtime()
            runtime.start()
            info = runtime.system_info.get_info()
            runtime.shutdown()

            return {
                "success": True,
                "message": "Core Runtime loaded and booted successfully.",
                "details": info
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Core Runtime verification failed: {str(e)}",
                "details": {}
            }

    def check_cli(self) -> Dict[str, Any]:
        """
        Verify that the CLI interface is configured and responsive.
        """
        try:
            from yasinai.cli.main import create_parser
            import argparse
            parser = create_parser()
            subcommands = []
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice in action.choices:
                        subcommands.append(choice)

            return {
                "success": len(subcommands) > 0,
                "message": "CLI parser instantiated successfully.",
                "subcommands_found": subcommands
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"CLI verification failed: {str(e)}",
                "subcommands_found": []
            }

    def check_security_platform(self) -> Dict[str, Any]:
        """
        Verify that Security Platform components are functional.
        """
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
            return {
                "success": success,
                "message": "Security Platform identity and encryption validated." if success else "Identity or encryption mismatch.",
                "identity_ok": user is not None,
                "encryption_ok": dec_data == "health_check_secret"
            }
        except Exception as e:
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
            return {
                "success": success,
                "message": "Knowledge Platform memory storage and retrieval validated." if success else "Memory storage or retrieval failed.",
                "memory_ok": len(short_mem) > 0,
                "search_ok": len(results) > 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Knowledge Platform verification failed: {str(e)}",
                "memory_ok": False,
                "search_ok": False
            }
