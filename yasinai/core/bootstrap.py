"""Module Discovery and Loader for YasinAI."""

import importlib
import os
import sys
import types
from typing import List, Any
from yasinai.core.system import SystemRegistry


class BootstrapManager:
    """Discovers and loads core and extension modules."""

    def __init__(self, registry: SystemRegistry) -> None:
        """Initialize BootstrapManager with a registry."""
        self.registry = registry
        self._loaded_modules: List[str] = []

    def load_module(self, module_name: str) -> Any:
        """Dynamically load/import a python module and register it if applicable."""
        try:
            if module_name in sys.modules:
                mod = sys.modules[module_name]
                if isinstance(mod, types.ModuleType):
                    module = importlib.reload(mod)
                else:
                    module = mod
            else:
                module = importlib.import_module(module_name)

            self._loaded_modules.append(module_name)

            # If the module has an initialization/register function, call it
            if hasattr(module, "register_service"):
                module.register_service(self.registry)
            elif hasattr(module, "initialize"):
                module.initialize(self.registry)

            return module
        except Exception as e:
            raise ImportError(f"Failed to bootstrap module {module_name}: {e}")

    def discover_modules(self, directory: str) -> List[str]:
        """Discover modules in a given directory."""
        discovered: List[str] = []
        if not os.path.exists(directory):
            return discovered

        for name in os.listdir(directory):
            full_path = os.path.join(directory, name)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
                discovered.append(name)
            elif name.endswith(".py") and name != "__init__.py":
                discovered.append(name[:-3])
        return discovered

    @property
    def loaded_modules(self) -> List[str]:
        """Get list of successfully loaded modules."""
        return self._loaded_modules
