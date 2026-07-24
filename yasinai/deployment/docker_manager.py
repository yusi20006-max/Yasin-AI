"""
Docker Manager for YasinAI Deployment System.
Handles Dockerfile/docker-compose generation, status check, and deployment configuration.
"""

import os
import shutil
import subprocess
from typing import Any, Dict


class DockerManager:
    """
    Manages Docker-related configuration, file generation, and system status checks.
    """

    def __init__(self, root_directory: str = "."):
        self.root_directory = root_directory

    def check_docker_available(self) -> bool:
        """
        Check if the docker command-line tool is installed.
        """
        return shutil.which("docker") is not None

    def check_docker_compose_available(self) -> bool:
        """
        Check if docker-compose or 'docker compose' is available.
        """
        if shutil.which("docker-compose") is not None:
            return True
        # Try running 'docker compose version'
        if self.check_docker_available():
            try:
                res = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
                return res.returncode == 0
            except Exception:
                return False
        return False

    def generate_docker_files(self, overwrite: bool = False) -> Dict[str, bool]:
        """
        Ensure Dockerfile and docker-compose.yml exist at the repository root.
        """
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
        if not os.path.exists(dockerfile_path) or overwrite:
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)
            dockerfile_created = True

        compose_created = False
        if not os.path.exists(compose_path) or overwrite:
            with open(compose_path, "w") as f:
                f.write(compose_content)
            compose_created = True

        return {
            "dockerfile_created": dockerfile_created,
            "compose_created": compose_created
        }

    def get_docker_status(self) -> Dict[str, Any]:
        """
        Get status of docker tools and files.
        """
        return {
            "docker_available": self.check_docker_available(),
            "docker_compose_available": self.check_docker_compose_available(),
            "dockerfile_exists": os.path.exists(os.path.join(self.root_directory, "Dockerfile")),
            "docker_compose_exists": os.path.exists(os.path.join(self.root_directory, "docker-compose.yml"))
        }
