import importlib
from typing import Any, List


class Bootstrap:
    """
    Handles dynamic module discovery, loading, and registration.
    """

    def __init__(self, runtime: Any) -> None:
        """
        Initialize the Bootstrap with the runtime instance.
        """
        self.runtime = runtime
        self.loaded_modules: List[str] = []

    def discover_and_load(self, module_names: List[str]) -> List[str]:
        """
        Dynamically import modules from a list of module names and execute
        their registration hook if available (e.g., register_module(runtime)).
        """
        loaded = []
        for name in module_names:
            try:
                mod = importlib.import_module(name)
                if hasattr(mod, "register_module") and callable(getattr(mod, "register_module")):
                    mod.register_module(self.runtime)

                loaded.append(name)
                self.loaded_modules.append(name)
            except Exception as e:
                raise ImportError(f"Failed to bootstrap and load module '{name}': {e}") from e
        return loaded
