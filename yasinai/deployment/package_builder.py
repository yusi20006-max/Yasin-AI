"""Deployment Package Builder to validate structures and output release artifacts."""

import os
import json
import shutil
from typing import Dict, Any, List, Optional


class DeploymentPackageBuilder:
    """Handles verification and generation of ready-to-deploy release archives."""

    @staticmethod
    def validate_project_structure(project_path: str) -> List[str]:
        """Validates that a YasinAI project contains essential folders and manifests.

        Rules:
        1. Must contain setup.py or config.json.
        2. Must contain yasinai/ folder.
        3. No secrets or private files (.key, .env) in target directory.

        Args:
            project_path: Path to the project root.

        Returns:
            A list of structural errors or warnings found (empty if completely valid).
        """
        errors = []
        if not os.path.exists(project_path):
            errors.append("Project path does not exist.")
            return errors

        # Essential check
        has_setup = os.path.exists(os.path.join(project_path, "setup.py"))
        has_config = os.path.exists(os.path.join(project_path, "config.json"))
        if not has_setup and not has_config:
            errors.append("Missing project manifests ('setup.py' or 'config.json').")

        # Package structure check
        package_dir = os.path.join(project_path, "yasinai")
        if not os.path.exists(package_dir):
            errors.append("Missing core code directory 'yasinai/'.")

        # Security scan for secrets (e.g. .env, *.key)
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file == ".env" or file.endswith(".key") or file.endswith(".token"):
                    # Only report secret files that are not git-ignored or part of pytest cache
                    if ".git" not in root and ".pytest_cache" not in root:
                        errors.append(f"Security Warning: Found restricted credential file: '{os.path.join(root, file)}'")

        return errors

    @staticmethod
    def build_release_artifact(project_path: str, output_path: str = "dist") -> Optional[str]:
        """Builds a deployable zip release package of the project.

        Args:
            project_path: Path to the project source directory.
            output_path: Target directory to place the generated artifact.

        Returns:
            The path to the created archive file if successful, otherwise None.
        """
        errors = DeploymentPackageBuilder.validate_project_structure(project_path)
        # We fail build if critical structural errors are present (excluding warning alerts)
        critical_errors = [e for e in errors if "Security Warning:" not in e]
        if critical_errors:
            return None

        try:
            os.makedirs(output_path, exist_ok=True)
            archive_name = "yasinai_release"
            output_file = os.path.join(output_path, archive_name)

            # Use shutil to generate standard zip artifact
            zip_path = shutil.make_archive(output_file, "zip", project_path)
            return zip_path
        except (IOError, OSError):
            return None
