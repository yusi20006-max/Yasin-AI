"""
Extension API for YasinAI Developer Platform.
Allows third-party systems to expose custom capabilities or hooks.
"""

from typing import Any, Dict, List, Optional


class ExtensionAPI:
    """
    Registry and entrypoint for external developer extensions.
    """

    def __init__(self) -> None:
        self._extensions: Dict[str, Dict[str, Any]] = {}

    def register_extension(self, name: str, ext_type: str, handler: Any) -> None:
        """
        Register a custom developer extension.
        """
        if name in self._extensions:
            raise ValueError(f"Extension '{name}' already registered.")

        self._extensions[name] = {
            "name": name,
            "type": ext_type,
            "handler": handler
        }

    def get_extension(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a registered extension dictionary.
        """
        return self._extensions.get(name)

    def invoke_extension(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke a registered extension's handler.
        """
        ext = self.get_extension(name)
        if not ext:
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
            return True
        return False

    def list_extensions(self) -> List[Dict[str, Any]]:
        """
        List all registered developer extensions.
        """
        return list(self._extensions.values())
