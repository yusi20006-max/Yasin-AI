import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Bootstrap:
    """Discover and load configured modules exactly once per runtime."""

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self.loaded_modules: list[str] = []

    def discover_and_load(self, module_names: list[str]) -> list[str]:
        """Import modules and invoke their optional registration hook.

        Duplicate module names are ignored while preserving configuration order.
        If a module fails, the exception is wrapped with the module name and
        modules successfully loaded before the failure remain recorded.
        """
        loaded: list[str] = []
        seen = set(self.loaded_modules)
        for name in module_names:
            if name in seen:
                logger.debug("Module already bootstrapped: '%s'", name)
                continue
            try:
                logger.debug("Attempting to bootstrap module: '%s'", name)
                mod = importlib.import_module(name)
                register = getattr(mod, "register_module", None)
                if register is not None:
                    if not callable(register):
                        raise TypeError("register_module is not callable")
                    register(self.runtime)
                loaded.append(name)
                self.loaded_modules.append(name)
                seen.add(name)
                logger.info("Successfully bootstrapped module: '%s'", name)
            except Exception as exc:
                logger.exception("Failed to bootstrap module '%s'", name)
                raise ImportError(f"Failed to bootstrap and load module '{name}': {exc}") from exc
        return loaded

    def reset(self) -> None:
        """Clear the per-runtime bootstrap registry."""
        self.loaded_modules.clear()
