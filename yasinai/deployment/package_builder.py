"""
Package Builder for YasinAI Deployment System.
Bundles modules, agents, and plugins into deployable artifacts.
"""
from __future__ import annotations

import logging
import os
import tarfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_INCLUDE_PATHS = (
    "yasinai/core/",
    "yasinai/cli/",
    "pyproject.toml",
)


class PackageBuilder:
    """Builds source-based deployment archives with safe archive member names."""

    def build_package(
        self,
        name: str,
        version: str = "1.0.0",
        output_directory: str = "dist/",
        *,
        include_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Bundle the given paths into a real .tar.gz deployment artifact.

        Source paths may be relative or absolute for backwards compatibility.
        Archive member names are always normalized to relative paths derived
        from a common source root, preventing absolute/``..`` traversal names
        from being emitted into the resulting tarball.
        """
        logger.info(
            "Building deployment package '%s' (version=%s) to directory '%s'...",
            name,
            version,
            output_directory,
        )
        paths_to_include = list(include_paths) if include_paths is not None else list(_DEFAULT_INCLUDE_PATHS)

        try:
            package_name = f"{name}-pkg-{version}.tar.gz" if "yasinai" in name else f"{name}-v{version}.tar.gz"
            os.makedirs(output_directory, exist_ok=True)
            archive_path = os.path.join(output_directory, package_name)

            resolved_paths = [(path, Path(path).resolve()) for path in paths_to_include if os.path.exists(path)]
            if resolved_paths:
                source_roots = [resolved.parent if resolved.is_file() else resolved.parent for _, resolved in resolved_paths]
                common_root = Path(os.path.commonpath([str(root) for root in source_roots]))
            else:
                common_root = Path.cwd().resolve()

            files_included: list[str] = []
            with tarfile.open(archive_path, "w:gz") as tar:
                for original_path, resolved_path in resolved_paths:
                    try:
                        arcname = resolved_path.relative_to(common_root).as_posix()
                    except ValueError as exc:
                        raise ValueError(f"cannot derive safe archive path for {original_path!r}") from exc
                    if not arcname or arcname == "." or arcname.startswith("/") or ".." in Path(arcname).parts:
                        raise ValueError(f"unsafe archive member path for {original_path!r}")
                    tar.add(str(resolved_path), arcname=arcname)
                    files_included.append(original_path)

                for path in paths_to_include:
                    if not os.path.exists(path):
                        logger.warning("Skipping missing path for package '%s': '%s'", name, path)

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
