"""Docker container detection, configuration, and orchestration helpers."""

import os
from typing import Dict, Any, List, Optional


class DockerManager:
    """Manages Docker environment detection and configuration helpers."""

    @staticmethod
    def is_in_docker() -> bool:
        """Detects whether the current process is running inside a Docker container.

        Returns:
            True if running inside Docker, False otherwise.
        """
        # Method 1: Check .dockerenv file
        if os.path.exists("/.dockerenv"):
            return True

        # Method 2: Check cgroup file
        cgroup_path = "/proc/self/cgroup"
        if os.path.exists(cgroup_path):
            try:
                with open(cgroup_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "docker" in content or "kubepods" in content:
                        return True
            except IOError:
                pass

        # Method 3: Check environment variables
        if os.environ.get("DOCKER_CONTAINER") or os.environ.get("YASINAI_DOCKER"):
            return True

        return False

    @staticmethod
    def generate_container_config(port: int = 8000, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generates helper configurations for deploying YasinAI in containers.

        Args:
            port: Exposed container port.
            env_vars: Environment variables to inject.

        Returns:
            A dictionary containing generated container parameters.
        """
        default_env = {
            "YASINAI_ENV": "production",
            "YASINAI_DOCKER": "true",
            "LOG_LEVEL": "INFO"
        }
        if env_vars:
            default_env.update(env_vars)

        return {
            "image": "yasinai:latest",
            "ports": {f"{port}/tcp": port},
            "environment": default_env,
            "volumes": {
                "/app/data": {
                    "bind": "/var/lib/yasinai",
                    "mode": "rw"
                }
            },
            "restart_policy": {"Name": "on-failure", "MaximumRetryCount": 5}
        }
