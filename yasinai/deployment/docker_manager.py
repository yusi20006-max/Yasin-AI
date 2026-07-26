"""
Docker Manager for YasinAI Deployment System.
Handles Dockerfile/docker-compose generation, status check, and deployment configuration.
"""

import logging
import os
import shutil
import subprocess
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DockerManager:
    """
    Manages Docker-related configuration, file generation, and system status checks.
    """

    def __init__(self, root_directory: str = "."):
        self.root_directory: str = root_directory

    def check_docker_available(self) -> bool:
        """
        Check if the docker command-line tool is installed.
        """
        logger.debug("Checking if Docker command-line tool is available...")
        available = shutil.which("docker") is not None
        logger.debug(f"Docker availability: {available}")
        return available

    def check_docker_compose_available(self) -> bool:
        """
        Check if docker-compose or 'docker compose' is available.
        """
        logger.debug("Checking if Docker Compose is available...")
        if shutil.which("docker-compose") is not None:
            logger.debug("Found 'docker-compose' binary in path.")
            return True
        # Try running 'docker compose version'
        if self.check_docker_available():
            try:
                res = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
                success = res.returncode == 0
                logger.debug(f"'docker compose' verification exit code: {res.returncode}")
                return success
            except Exception as e:
                logger.warning(f"Error while invoking 'docker compose version': {e}")
                return False
        logger.debug("Docker Compose is not available.")
        return False

    def generate_docker_files(self, overwrite: bool = False) -> Dict[str, bool]:
        """
        Ensure Dockerfile and docker-compose.yml exist at the repository root.
        """
        logger.info(f"Generating Docker files in target directory '{self.root_directory}' (overwrite={overwrite})...")
        dockerfile_path = os.path.join(self.root_directory, "Dockerfile")
        compose_path = os.path.join(self.root_directory, "docker-compose.yml")

        dockerfile_content = (
            "FROM python:3.12-slim\n\n"
            "WORKDIR /app\n\n"
            "COPY pyproject.toml README.md ./\n"
            "RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false\n\n"
            "COPY . .\n"
            "RUN poetry install --no-root && pip install .\n\n"
            "EXPOSE 8000\n\n"
            'CMD ["yasin", "status"]\n'
        )

        compose_content = (
            "version: '3.8'\n\n"
            "services:\n"
            "  yasinai:\n"
            "    build: .\n"
            "    container_name: yasinai-container\n"
            "    ports:\n"
            "      - \"8000:8000\"\n"
            "    environment:\n"
            "      - ENVIRONMENT=production\n"
        )

        dockerfile_created = False
        try:
            if not os.path.exists(dockerfile_path) or overwrite:
                with open(dockerfile_path, "w", encoding="utf-8") as f:
                    f.write(dockerfile_content)
                dockerfile_created = True
                logger.info(f"Created Dockerfile at: {dockerfile_path}")
        except IOError as e:
            logger.error(f"Failed to write Dockerfile: {e}", exc_info=True)

        compose_created = False
        try:
            if not os.path.exists(compose_path) or overwrite:
                with open(compose_path, "w", encoding="utf-8") as f:
                    f.write(compose_content)
                compose_created = True
                logger.info(f"Created docker-compose.yml at: {compose_path}")
        except IOError as e:
            logger.error(f"Failed to write docker-compose.yml: {e}", exc_info=True)

        return {
            "dockerfile_created": dockerfile_created,
            "compose_created": compose_created
        }

    def get_docker_status(self) -> Dict[str, Any]:
        """
        Get status of docker tools and files.
        """
        logger.debug("Retrieving Docker deployment status...")
        status = {
            "docker_available": self.check_docker_available(),
            "docker_compose_available": self.check_docker_compose_available(),
            "dockerfile_exists": os.path.exists(os.path.join(self.root_directory, "Dockerfile")),
            "docker_compose_exists": os.path.exists(os.path.join(self.root_directory, "docker-compose.yml"))
        }
        logger.debug(f"Docker status results: {status}")
        return status
