"""Project installer, initialization, and environment validation."""

import os
import json
import sys
from typing import Dict, Any, List


class Installer:
    """Manages the installation, configuration initialization, and environment check for YasinAI."""

    def __init__(self, target_dir: str = "."):
        """Initializes the installer.

        Args:
            target_dir: The directory where YasinAI configuration and assets should be installed.
        """
        self.target_dir = target_dir

    def validate_environment(self) -> Dict[str, Any]:
        """Validates that the host environment meets YasinAI requirements.

        Returns:
            A dictionary containing status, python version, and system readiness metrics.
        """
        python_version = sys.version_info
        is_python_supported = python_version.major >= 3 and python_version.minor >= 8

        # Check write permissions (of target_dir, or closest existing ancestor)
        check_path = self.target_dir
        while check_path and not os.path.exists(check_path):
            parent = os.path.dirname(check_path)
            if parent == check_path: # reached root
                break
            check_path = parent

        is_writable = os.access(check_path or ".", os.W_OK)

        # Check common system binaries/folders
        issues = []
        if not is_python_supported:
            issues.append(f"Python {python_version.major}.{python_version.minor} is not officially supported. (Python >= 3.8 is required)")
        if not is_writable:
            issues.append(f"Target directory '{self.target_dir}' is not writable.")

        return {
            "ready": len(issues) == 0,
            "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "is_writable": is_writable,
            "issues": issues
        }

    def initialize_configuration(self) -> bool:
        """Generates default config files in the target directory.

        Returns:
            True if configuration is written successfully, False otherwise.
        """
        try:
            os.makedirs(self.target_dir, exist_ok=True)
            config_path = os.path.join(self.target_dir, "config.json")

            # Prevent overwriting existing user configuration
            if os.path.exists(config_path):
                return True

            default_config = {
                "system": {
                    "name": "YasinAI",
                    "version": "1.0.0",
                    "environment": "production"
                },
                "platforms": {
                    "developer_platform": {"enabled": True},
                    "security_platform": {"enabled": True, "security_level": "standard"},
                    "knowledge_platform": {"enabled": True, "storage": "local"},
                    "deployment": {"enabled": True}
                },
                "logging": {
                    "level": "INFO",
                    "file": "yasinai.log"
                }
            }

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            return True
        except (IOError, OSError):
            return False

    def install(self) -> Dict[str, Any]:
        """Executes full environment validation and initializes platform configurations.

        Returns:
            A dictionary summary with installation status.
        """
        env_report = self.validate_environment()
        if not env_report["ready"]:
            return {
                "success": False,
                "message": "Environment validation failed.",
                "issues": env_report["issues"]
            }

        config_success = self.initialize_configuration()
        if not config_success:
            return {
                "success": False,
                "message": "Failed to initialize configuration files.",
                "issues": ["IO error during config generation."]
            }

        return {
            "success": True,
            "message": "YasinAI installed and configured successfully.",
            "issues": []
        }
