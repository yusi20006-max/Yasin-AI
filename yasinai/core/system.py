import logging
import platform
import sys
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SystemInfo:
    """
    Provides key information about the running YasinAI system and its environment.
    """

    def __init__(self, app_name: str = "YasinAI", version: str = "1.1.2", status: str = "unknown") -> None:
        self.app_name: str = app_name
        self.version: str = version
        self.status: str = status

    def get_info(self) -> Dict[str, Any]:
        """
        Get system and environment details.
        """
        try:
            return {
                "app_name": self.app_name,
                "version": self.version,
                "status": self.status,
                "python_version": sys.version,
                "platform": platform.platform(),
                "os": platform.system(),
                "architecture": platform.machine(),
            }
        except Exception as e:
            logger.error(f"Failed to gather system information: {e}", exc_info=True)
            # Return basic fallback information to ensure non-breaking behavior
            return {
                "app_name": self.app_name,
                "version": self.version,
                "status": self.status,
                "python_version": sys.version,
                "platform": "Unknown",
                "os": "Unknown",
                "architecture": "Unknown",
            }


class ServiceRegistry:
    """
    A service registry to register and manage core services within the runtime.
    """

    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}

    def register_service(self, name: str, service: Any, overwrite: bool = False) -> None:
        """
        Register a service with a unique name.
        """
        if name in self._services and not overwrite:
            msg = f"Service '{name}' is already registered. Use overwrite=True to replace it."
            logger.error(msg)
            raise ValueError(msg)
        self._services[name] = service
        logger.debug(f"Service '{name}' successfully registered.")

    def get_service(self, name: str) -> Any:
        """
        Retrieve a registered service by its name.
        """
        if name not in self._services:
            msg = f"Service '{name}' not found in the registry."
            logger.error(msg)
            raise KeyError(msg)
        return self._services[name]

    def has_service(self, name: str) -> bool:
        """
        Check if a service is registered.
        """
        return name in self._services

    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service from the registry.
        """
        if name in self._services:
            del self._services[name]
            logger.debug(f"Service '{name}' unregistered successfully.")
            return True
        logger.warning(f"Attempted to unregister non-existent service: '{name}'")
        return False

    def list_services(self) -> Dict[str, Any]:
        """
        Return all registered services.
        """
        return self._services.copy()
