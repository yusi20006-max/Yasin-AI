"""Package Builder for YasinAI."""

import json
import os
import zipfile
from pathlib import Path
from typing import Tuple, List


class PackageBuilder:
    """Validates and builds developer packages as distributable zip archives."""

    @staticmethod
    def validate_package(package_path: str) -> Tuple[bool, List[str]]:
        """Validate package directory structure.

        Requires:
        - config.json
        - src/ directory with at least one Python file or entrypoint definition.
        """
        path = Path(package_path)
        errors = []

        if not path.exists() or not path.is_dir():
            return False, ["Package path does not exist or is not a directory."]

        # Check config.json
        config_file = path / "config.json"
        if not config_file.exists():
            errors.append("Missing required 'config.json' file.")
        else:
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                if "name" not in config:
                    errors.append("config.json is missing the 'name' field.")
                if "version" not in config:
                    errors.append("config.json is missing the 'version' field.")
            except (json.JSONDecodeError, IOError) as e:
                errors.append(f"Invalid or unreadable config.json: {str(e)}")

        # Check src/ directory
        src_dir = path / "src"
        if not src_dir.exists() or not src_dir.is_dir():
            errors.append("Missing required 'src/' directory.")

        return len(errors) == 0, errors

    @staticmethod
    def build_package(package_path: str, output_dir: str = "dist") -> str:
        """Validate package and build a zip distribution.

        Returns path to the generated archive.
        """
        is_valid, errors = PackageBuilder.validate_package(package_path)
        if not is_valid:
            raise ValueError(f"Package validation failed: {', '.join(errors)}")

        path = Path(package_path)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # Get package details
        with open(path / "config.json", "r") as f:
            config = json.load(f)
        pkg_name = config["name"].lower().replace(" ", "_").replace("-", "_")
        pkg_version = config["version"]

        zip_filename = out_path / f"{pkg_name}-{pkg_version}.zip"

        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_path):
                # Avoid writing unnecessary build artifacts or cache files
                if "__pycache__" in root or ".pytest_cache" in root:
                    continue
                for file in files:
                    file_path = Path(root) / file
                    # Calculate relative path
                    rel_path = file_path.relative_to(package_path)
                    zipf.write(file_path, rel_path)

        return str(zip_filename)
