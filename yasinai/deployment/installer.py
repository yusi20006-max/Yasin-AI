"""
Installer for YasinAI Deployment System.
Handles local setup, directory creation, configuration template setup, and environment verification.
"""

import logging
import os
import sys
import json
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Installer:
    """
    Automates and guides the installation and configuration of YasinAI locally.
    """

    def __init__(self, target_directory: str = "."):
        self.target_directory: str = target_directory

    def verify_environment(self) -> Dict[str, Any]:
        """
        Verify the system environment meets prerequisites (Python version, write permissions).
        """
        logger.debug("Verifying local installation environment prerequisites...")
        python_ver = sys.version_info
        python_ok: bool = python_ver.major >= 3 and python_ver.minor >= 8
        python_str = f"{python_ver.major}.{python_ver.minor}.{python_ver.micro}"

        # Check write permission in target directory
        write_ok: bool = os.access(self.target_directory, os.W_OK)
        target_path: str = os.path.abspath(self.target_directory)

        success: bool = python_ok and write_ok
        logger.debug(f"Environment verification status: python_ok={python_ok}, write_ok={write_ok} (success={success})")

        return {
            "success": success,
            "python_version": python_str,
            "python_ok": python_ok,
            "write_ok": write_ok,
            "target_directory": target_path
        }

    def setup_directories(self) -> List[str]:
        """
        Create necessary system directories.
        """
        logger.info("Setting up system directories for YasinAI...")
        directories = [
            os.path.join(self.target_directory, "dist"),
            os.path.join(self.target_directory, "logs"),
            os.path.join(self.target_directory, "config"),
        ]
        created: List[str] = []
        for d in directories:
            if not os.path.exists(d):
                try:
                    os.makedirs(d, exist_ok=True)
                    created.append(d)
                    logger.info(f"Created directory: {d}")
                except Exception as e:
                    logger.error(f"Failed to create directory '{d}': {e}", exc_info=True)
        return created

    def install(self) -> Dict[str, Any]:
        """
        Execute the full automated setup.
        """
        logger.info("Executing YasinAI local installation...")
        env_status = self.verify_environment()
        if not env_status["success"]:
            logger.error("Local installation aborted: environment verification failed.")
            return {
                "success": False,
                "message": "Environment verification failed.",
                "details": env_status
            }

        created_dirs = self.setup_directories()

        # Write a default config template if configuration directory is empty or if config.json does not exist
        config_path = os.path.join(self.target_directory, "config", "config.json")
        config_created = False
        if not os.path.exists(config_path):
            try:
                from yasinai import __version__ as _pkg_version
            except Exception:
                try:
                    from importlib.metadata import version as _meta_version
                    _pkg_version = _meta_version("yasinai")
                except Exception:
                    _pkg_version = "0.0.0"
            default_config = {
                "app_name": "YasinAI",
                "version": _pkg_version,
                "debug": False,
                "modules": []
            }
            try:
                # Ensure parent folder exists
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=4)
                config_created = True
                logger.info(f"Created default configuration template at: {config_path}")
            except IOError as e:
                logger.error(f"Failed to create configuration file template at '{config_path}': {e}", exc_info=True)

        logger.info("YasinAI local installation successfully completed.")
        return {
            "success": True,
            "message": "YasinAI local installation completed successfully.",
            "verified_env": env_status,
            "created_directories": created_dirs,
            "config_created": config_created
        }
