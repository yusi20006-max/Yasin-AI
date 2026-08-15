"""
Docker Manager for YasinAI Deployment System.
Handles Dockerfile/docker-compose generation, status check, and deployment configuration.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Scaffold templates aligned with production hardening (non-root, healthcheck).
# Real production deploy profile remains deploy/compose.production.yml — never clobber
# an existing repo-root Dockerfile without confirm_overwrite_production=True.
_HARDENED_DOCKERFILE = """FROM python:3.12-slim

WORKDIR /app

# Secrets must never be baked into the image.
COPY pyproject.toml README.md LICENSE ./
COPY yasinai ./yasinai
COPY security_platform ./security_platform
COPY developer_platform ./developer_platform
COPY knowledge_platform ./knowledge_platform
COPY api_service ./api_service
COPY observability ./observability

RUN python -m pip install --no-cache-dir --upgrade pip \\
    && python -m pip install --no-cache-dir . \\
    && useradd --system --uid 10001 --no-create-home yasinai \\
    && chown -R yasinai:yasinai /app

COPY --chown=yasinai:yasinai . .

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \\
  CMD yasin status || exit 1

CMD ["yasin", "status"]
"""

_HARDENED_COMPOSE = """version: "3.8"

# Scaffolded compose. For production hardening prefer:
#   docker compose -f deploy/compose.production.yml up

services:
  yasinai:
    build: .
    container_name: yasinai-container
    ports:
      - "8000:8000"
    environment:
      - YASINAI_ENVIRONMENT=development
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: false
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m
    healthcheck:
      test: ["CMD", "yasin", "status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
"""


class DockerManager:
    """
    Manages Docker-related configuration, file generation, and system status checks.
    """

    def __init__(self, root_directory: str = "."):
        self.root_directory: str = root_directory

    def check_docker_available(self) -> bool:
        """Check if the docker command-line tool is installed."""
        logger.debug("Checking if Docker command-line tool is available...")
        available = shutil.which("docker") is not None
        logger.debug(f"Docker availability: {available}")
        return available

    def check_docker_compose_available(self) -> bool:
        """Check if docker-compose or 'docker compose' is available."""
        logger.debug("Checking if Docker Compose is available...")
        if shutil.which("docker-compose") is not None:
            logger.debug("Found 'docker-compose' binary in path.")
            return True
        if self.check_docker_available():
            try:
                res = subprocess.run(
                    ["docker", "compose", "version"],
                    capture_output=True,
                    text=True,
                )
                success = res.returncode == 0
                logger.debug(f"'docker compose' verification exit code: {res.returncode}")
                return success
            except Exception as e:
                logger.warning(f"Error while invoking 'docker compose version': {e}")
                return False
        logger.debug("Docker Compose is not available.")
        return False

    def generate_docker_files(
        self,
        overwrite: bool = False,
        *,
        confirm_overwrite_production: bool = False,
    ) -> Dict[str, bool]:
        """
        Ensure Dockerfile and docker-compose.yml exist under ``root_directory``.

        Existing files are **never** overwritten unless both ``overwrite=True``
        **and** ``confirm_overwrite_production=True``. A single boolean must
        not be able to silently replace hardened production Docker files.

        Generated templates follow current hardening conventions (non-root
        USER 10001, HEALTHCHECK, cap_drop / no-new-privileges in compose,
        YASINAI_* env prefix).
        """
        logger.info(
            "Generating Docker files in '%s' (overwrite=%s, confirm_overwrite_production=%s)",
            self.root_directory,
            overwrite,
            confirm_overwrite_production,
        )
        dockerfile_path = os.path.join(self.root_directory, "Dockerfile")
        compose_path = os.path.join(self.root_directory, "docker-compose.yml")

        dockerfile_created = self._write_if_allowed(
            dockerfile_path,
            _HARDENED_DOCKERFILE,
            overwrite=overwrite,
            confirm_overwrite_production=confirm_overwrite_production,
            label="Dockerfile",
        )
        compose_created = self._write_if_allowed(
            compose_path,
            _HARDENED_COMPOSE,
            overwrite=overwrite,
            confirm_overwrite_production=confirm_overwrite_production,
            label="docker-compose.yml",
        )

        return {
            "dockerfile_created": dockerfile_created,
            "compose_created": compose_created,
        }

    def _write_if_allowed(
        self,
        path: str,
        content: str,
        *,
        overwrite: bool,
        confirm_overwrite_production: bool,
        label: str,
    ) -> bool:
        exists = os.path.exists(path)
        if exists and not overwrite:
            logger.debug("Skipping existing %s (overwrite=False)", label)
            return False
        if exists and overwrite and not confirm_overwrite_production:
            logger.warning(
                "Refusing to overwrite existing %s at %s without "
                "confirm_overwrite_production=True (protects production hardening)",
                label,
                path,
            )
            return False
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Wrote %s at: %s", label, path)
            return True
        except OSError as e:
            logger.error("Failed to write %s: %s", label, e, exc_info=True)
            return False

    def get_docker_status(self) -> Dict[str, Any]:
        """Get status of docker tools and files."""
        logger.debug("Retrieving Docker deployment status...")
        status = {
            "docker_available": self.check_docker_available(),
            "docker_compose_available": self.check_docker_compose_available(),
            "dockerfile_exists": os.path.exists(
                os.path.join(self.root_directory, "Dockerfile")
            ),
            "docker_compose_exists": os.path.exists(
                os.path.join(self.root_directory, "docker-compose.yml")
            ),
        }
        logger.debug(f"Docker status results: {status}")
        return status
