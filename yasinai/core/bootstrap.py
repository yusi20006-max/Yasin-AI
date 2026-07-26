import importlib
import logging
from typing import Any, List

logger = logging.getLogger(__name__)


class Bootstrap:
    """
    Handles dynamic module discovery, loading, and registration.
    """

    def __init__(self, runtime: Any) -> None:
        """
        Initialize the Bootstrap with the runtime instance.
        """
        self.runtime: Any = runtime
        self.loaded_modules: List[str] = []

    def discover_and_load(self, module_names: List[str]) -> List[str]:
        """
        Dynamically import modules from a list of module names and execute
        their registration hook if available (e.g., register_module(runtime)).
        """
        loaded: List[str] = []
        for name in module_names:
            try:
                logger.debug(f"Attempting to bootstrap module: '{name}'")
                mod = importlib.import_module(name)
                if hasattr(mod, "register_module") and callable(getattr(mod, "register_module")):
                    logger.debug(f"Executing register_module for: '{name}'")
                    mod.register_module(self.runtime)

                loaded.append(name)
                self.loaded_modules.append(name)
                logger.info(f"Successfully bootstrapped and loaded module: '{name}'")
            except Exception as e:
                logger.error(f"Failed to bootstrap and load module '{name}': {e}", exc_info=True)
                raise ImportError(f"Failed to bootstrap and load module '{name}': {e}") from e
        return loaded
