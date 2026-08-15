"""
Package Builder for YasinAI Deployment System.
Bundles modules, agents, and plugins into deployable artifacts.
"""
from __future__ import annotations

import logging
import os
import tarfile
from pathlib import PurePath
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_INCLUDE_PATHS = (
    "yasinai/core/",
    "yasinai/cli/",
    "pyproject.toml",
)


class PackageBuilder:
    """Builds local, source-based deployment archives."""

    def build_package(
        self,
        name: str,
        version: str = "1.0.0",
        output_directory: str = "dist/",
        *,
        include_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Bundle the given repository-relative paths into a real .tar.gz artifact.

        ``include_paths`` must be relative paths and may not contain ``..``.
        This keeps the packaging surface confined to the current working tree
        and prevents callers from accidentally archiving arbitrary host files.
        """
        logger.info(
            "Building deployment package '%s' (version=%s) to directory '%s'...",
            name,
            version,
            output_directory,
        )
        paths_to_include = list(include_paths) if include_paths is not None else list(_DEFAULT_INCLUDE_PATHS)

        try:
            for path in paths_to_include:
                pure = PurePath(path)
                if pure.is_absolute() or ".." in pure.parts:
                    raise ValueError(f"include path must stay within the working tree: {path!r}")

            package_name = f"{name}-pkg-{version}.tar.gz" if "yasinai" in name else f"{name}-v{version}.tar.gz"
            os.makedirs(output_directory, exist_ok=True)
            archive_path = os.path.join(output_directory, package_name)

            files_included: list[str] = []
            with tarfile.open(archive_path, "w:gz") as tar:
                for path in paths_to_include:
                    if not os.path.exists(path):
                        logger.warning("Skipping missing path for package '%s': '%s'", name, path)
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
            logger.info("Package successfully built: %s", archive_path)
            return result
        except Exception:
            logger.exception("Failed to build package '%s'", name)
            return {
                "success": False,
                "package_name": "",
                "output_directory": output_directory,
                "archive_path": "",
                "version": version,
                "files_included": [],
            }
