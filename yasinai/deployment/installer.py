"""
Installer for YasinAI Deployment System.
Handles local setup, directory creation, configuration template setup, and environment verification.
"""

import os
import sys
import json
from typing import Any, Dict, List


class Installer:
    """
    Automates and guides the installation and configuration of YasinAI locally.
    """

    def __init__(self, target_directory: str = "."):
        self.target_directory = target_directory

    def verify_environment(self) -> Dict[str, Any]:
        """
        Verify the system environment meets prerequisites (Python version, write permissions).
        """
        python_ver = sys.version_info
        python_ok = python_ver.major >= 3 and python_ver.minor >= 8
        python_str = f"{python_ver.major}.{python_ver.minor}.{python_ver.micro}"

        # Check write permission in target directory
        write_ok = os.access(self.target_directory, os.W_OK)

        return {
            "success": python_ok and write_ok,
            "python_version": python_str,
            "python_ok": python_ok,
            "write_ok": write_ok,
            "target_directory": os.path.abspath(self.target_directory)
        }

    def setup_directories(self) -> List[str]:
        """
        Create necessary system directories.
        """
        directories = [
            os.path.join(self.target_directory, "dist"),
            os.path.join(self.target_directory, "logs"),
            os.path.join(self.target_directory, "config"),
        ]
        created = []
        for d in directories:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                created.append(d)
        return created

    def install(self) -> Dict[str, Any]:
        """
        Execute the full automated setup.
        """
        env_status = self.verify_environment()
        if not env_status["success"]:
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
            default_config = {
                "app_name": "YasinAI",
                "version": "1.0.0",
                "debug": False,
                "modules": []
            }
            try:
                # Ensure parent folder exists
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                config_created = True
            except IOError:
                pass

        return {
            "success": True,
            "message": "YasinAI local installation completed successfully.",
            "verified_env": env_status,
            "created_directories": created_dirs,
            "config_created": config_created
        }
