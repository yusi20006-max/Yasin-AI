"""
Extension API for YasinAI Developer Platform.
Allows third-party systems to expose custom capabilities or hooks.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ExtensionAPI:
    """
    Registry and entrypoint for external developer extensions.
    """

    def __init__(self) -> None:
        self._extensions: dict[str, dict[str, Any]] = {}

    def register_extension(self, name: str, ext_type: str, handler: Any) -> None:
        """
        Register a custom developer extension.
        """
        if name in self._extensions:
            logger.error(f"Cannot register extension: '{name}' is already registered.")
            raise ValueError(f"Extension '{name}' already registered.")

        self._extensions[name] = {
            "name": name,
            "type": ext_type,
            "handler": handler
        }
        logger.info(f"Successfully registered developer extension: '{name}' of type '{ext_type}'")

    def get_extension(self, name: str) -> dict[str, Any] | None:
        """
        Retrieve a registered extension dictionary.
        """
        return self._extensions.get(name)

    def invoke_extension(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke a registered extension's handler.
        """
        logger.debug(f"Invoking extension '{name}' with args={args}, kwargs={kwargs}")
        ext = self.get_extension(name)
        if not ext:
            logger.error(f"Cannot invoke extension '{name}': extension is not registered.")
            raise ValueError(f"Extension '{name}' is not registered.")

        handler = ext["handler"]
        if callable(handler):
            return handler(*args, **kwargs)
        return handler

    def unregister_extension(self, name: str) -> bool:
        """
        Unregister an extension by name.
        """
        if name in self._extensions:
            del self._extensions[name]
            logger.info(f"Successfully unregistered extension: '{name}'")
            return True
        logger.warning(f"Attempted to unregister non-existent extension: '{name}'")
        return False

    def list_extensions(self) -> list[dict[str, Any]]:
        """
        List all registered developer extensions.
        """
        return list(self._extensions.values())
