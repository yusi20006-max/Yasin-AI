"""System Information and Service Registry for YasinAI."""

import sys
from typing import Any, Dict, Optional


class SystemInfo:
    """YasinAI System Information class."""

    @property
    def version(self) -> str:
        """Return YasinAI version."""
        return "1.0.0"

    @property
    def python_version(self) -> str:
        """Return current Python version."""
        return sys.version

    @property
    def platform(self) -> str:
        """Return system platform."""
        return sys.platform


class SystemRegistry:
    """YasinAI System Service/Module Registry."""

    def __init__(self) -> None:
        """Initialize the system registry."""
        self._services: Dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """Register a service under a unique name."""
        self._services[name] = service

    def unregister(self, name: str) -> None:
        """Unregister a service."""
        if name in self._services:
            del self._services[name]

    def get(self, name: str) -> Optional[Any]:
        """Retrieve a service from the registry."""
        return self._services.get(name)

    def list_services(self) -> Dict[str, Any]:
        """List all registered services."""
        return self._services.copy()
