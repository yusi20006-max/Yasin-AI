"""
Package Builder for YasinAI Deployment System.
Bundles modules, agents, and plugins into deployable artifacts.
"""

import logging
import os
import tarfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_INCLUDE_PATHS = (
    "yasinai/core/",
    "yasinai/cli/",
    "pyproject.toml",
)


class PackageBuilder:
    """
    Manages packaging of plugins, agents, and platform integrations for distribution.
    """

    def build_package(
        self,
        name: str,
        version: str = "1.0.0",
        output_directory: str = "dist/",
        *,
        include_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Bundle the given paths into a real .tar.gz deployment artifact.

        include_paths defaults to the platform's core/cli/pyproject.toml
        files if not given, preserving prior behavior. Pass a different
        list to package a different set of components (e.g. a single
        plugin directory).
        """
        logger.info(f"Building deployment package '{name}' (version={version}) to directory '{output_directory}'...")
        paths_to_include = list(include_paths) if include_paths is not None else list(_DEFAULT_INCLUDE_PATHS)

        try:
            package_name = f"{name}-pkg-{version}.tar.gz" if "yasinai" in name else f"{name}-v{version}.tar.gz"
            os.makedirs(output_directory, exist_ok=True)
            archive_path = os.path.join(output_directory, package_name)

            files_included: List[str] = []
            with tarfile.open(archive_path, "w:gz") as tar:
                for path in paths_to_include:
                    if not os.path.exists(path):
                        logger.warning(f"Skipping missing path for package '{name}': '{path}'")
                        continue
                    tar.add(path, arcname=path)
                    files_included.append(path)

            result = {
                "success": True,
                "package_name": package_name,
                "output_directory": output_directory,
                "archive_path": os.path.abspath(archive_path),
                "version": version,
                "files_included": files_included,
            }
            logger.info(f"Package successfully built: {archive_path}")
            return result
        except Exception as e:
            logger.error(f"Failed to build package '{name}': {e}", exc_info=True)
            return {
                "success": False,
                "package_name": "",
                "output_directory": output_directory,
                "archive_path": "",
                "version": version,
                "files_included": [],
            }
