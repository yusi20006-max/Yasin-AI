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
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]


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

        When ``include_paths`` is omitted, the builder resolves its default
        source paths relative to the Yasin-AI package/repository root rather
        than the caller's current working directory. Explicit paths remain
        relative to the caller's cwd (for backwards compatibility) or may be
        absolute.

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
        using_defaults = include_paths is None
        paths_to_include = list(_DEFAULT_INCLUDE_PATHS if using_defaults else include_paths)

        try:
            package_name = f"{name}-pkg-{version}.tar.gz" if "yasinai" in name else f"{name}-v{version}.tar.gz"
            os.makedirs(output_directory, exist_ok=True)
            archive_path = os.path.join(output_directory, package_name)

            def resolve_source(path: str) -> Path:
                candidate = Path(path)
                if candidate.is_absolute():
                    return candidate.resolve()
                base = _PACKAGE_ROOT if using_defaults else Path.cwd()
                return (base / candidate).resolve()

            resolved_paths = [
                (path, resolved)
                for path in paths_to_include
                for resolved in [resolve_source(path)]
                if resolved.exists()
            ]
            common_root = (
                Path(os.path.commonpath([str(resolved.parent) for _, resolved in resolved_paths]))
                if resolved_paths
                else Path.cwd().resolve()
            )

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
                    if not resolve_source(path).exists():
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
