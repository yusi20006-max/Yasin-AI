"""Package builder and validation utility for distributable modules."""

import os
import json
import shutil
from typing import Dict, Any, List, Optional


class PackageBuilder:
    """Validates module structures and constructs distributable outputs."""

    @staticmethod
    def validate_package(package_dir: str) -> List[str]:
        """Validates that a package directory meets platform requirements.

        Rules:
        1. Must contain config.json.
        2. Must contain agent.py or plugin.py.
        3. config.json must contain name, version, and description.

        Args:
            package_dir: Path to directory being validated.

        Returns:
            A list of errors (empty if completely valid).
        """
        errors = []
        if not os.path.exists(package_dir):
            errors.append("Package directory does not exist.")
            return errors

        # 1. Config validation
        config_path = os.path.join(package_dir, "config.json")
        if not os.path.exists(config_path):
            errors.append("Missing required 'config.json' descriptor.")
        else:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Check fields
                for field in ["name", "version", "description"]:
                    if field not in config or not config[field]:
                        errors.append(f"config.json missing required metadata key: '{field}'.")
            except (json.JSONDecodeError, IOError):
                errors.append("Failed to load or parse 'config.json' as valid JSON.")

        # 2. Executable code check
        agent_path = os.path.join(package_dir, "agent.py")
        plugin_path = os.path.join(package_dir, "plugin.py")
        if not os.path.exists(agent_path) and not os.path.exists(plugin_path):
            errors.append("Package must define at least one executable component ('agent.py' or 'plugin.py').")

        return errors

    @staticmethod
    def build_package(package_dir: str, output_dir: str) -> Optional[str]:
        """Validates and packages developer directories into compressed zip assets.

        Args:
            package_dir: Directory containing code to build.
            output_dir: Directory where zipped asset is generated.

        Returns:
            Path to the zipped bundle file if successful, otherwise None.
        """
        errors = PackageBuilder.validate_package(package_dir)
        if errors:
            return None

        try:
            # Ensure output dir exists
            os.makedirs(output_dir, exist_ok=True)

            # Read config to fetch bundle name
            config_path = os.path.join(package_dir, "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            name = config["name"].lower().replace(" ", "_")
            version = config["version"].replace(".", "_")
            zip_base_name = f"{name}_{version}"

            # Create zip archive using shutil
            output_base = os.path.join(output_dir, zip_base_name)
            archive_path = shutil.make_archive(output_base, "zip", package_dir)
            return archive_path
        except (IOError, OSError):
            return None
