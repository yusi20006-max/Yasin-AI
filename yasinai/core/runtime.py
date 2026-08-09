import logging
from typing import Any, Dict, Optional

from yasinai.core.bootstrap import Bootstrap
from yasinai.core.config import Config
from yasinai.core.system import ServiceRegistry, SystemInfo

logger = logging.getLogger(__name__)


class Runtime:
    """Central execution engine of YasinAI with an explicit lifecycle."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    INITIALIZING = "INITIALIZING"
    REGISTERING_MODULES = "REGISTERING_MODULES"
    READY = "READY"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    FAILED = "FAILED"

    def __init__(self, config_defaults: Optional[Dict[str, Any]] = None) -> None:
        self.config: Config = Config(defaults=config_defaults)
        self.services: ServiceRegistry = ServiceRegistry()
        self.system_info: SystemInfo = SystemInfo(
            app_name=self.config.get("app_name", "YasinAI"),
            version=self.config.get("version", "1.0.0"),
            status="inactive",
        )
        self.bootstrap_loader: Bootstrap = Bootstrap(self)
        self.state = self.STOPPED
        self.last_error: Optional[str] = None

    def start(self) -> None:
        """Start the runtime; repeated starts while ready are harmless."""
        if self.state == self.READY:
            logger.debug("Runtime is already ready; start is a no-op")
            return
        if self.state != self.STOPPED:
            raise RuntimeError(f"Cannot start from state: {self.state}")

        try:
            self.startup()
            self.bootstrap()
            self.initialize()
            self.register_modules()
            self.ready()
        except Exception as exc:
            self.last_error = str(exc)
            self.state = self.FAILED
            self.system_info.status = "failed"
            self._cleanup_services()
            logger.error("Runtime startup failed", exc_info=True)
            raise RuntimeError(f"Runtime startup failed: {exc}") from exc

        logger.info("Core Runtime successfully started and ready.")

    def startup(self) -> None:
        if self.state != self.STOPPED:
            raise RuntimeError(f"Cannot startup from state: {self.state}")
        self.state = self.STARTING
        self.system_info.status = "starting"
        self.services.register_service("config", self.config, overwrite=True)
        self.services.register_service("system_info", self.system_info, overwrite=True)

    def bootstrap(self) -> None:
        if self.state != self.STARTING:
            raise RuntimeError(f"Cannot bootstrap from state: {self.state}")
        self.state = self.BOOTSTRAPPING
        self.bootstrap_loader.discover_and_load(self.config.get("modules", []))

    def initialize(self) -> None:
        if self.state != self.BOOTSTRAPPING:
            raise RuntimeError(f"Cannot initialize from state: {self.state}")
        self.state = self.INITIALIZING

    def register_modules(self) -> None:
        if self.state != self.INITIALIZING:
            raise RuntimeError(f"Cannot register modules from state: {self.state}")
        self.state = self.REGISTERING_MODULES

    def ready(self) -> None:
        if self.state != self.REGISTERING_MODULES:
            raise RuntimeError(f"Cannot set ready from state: {self.state}")
        self.state = self.READY
        self.system_info.status = "ready"
        self.last_error = None
        self.services.register_service("runtime", self, overwrite=True)

    def shutdown(self) -> None:
        """Gracefully stop the runtime; shutdown is safe to call repeatedly."""
        if self.state == self.STOPPED:
            return
        self.state = self.SHUTTING_DOWN
        self.system_info.status = "shutdown"
        self._cleanup_services()
        self.state = self.STOPPED
        logger.info("Runtime gracefully stopped.")

    def _cleanup_services(self) -> None:
        """Best-effort cleanup used by both normal shutdown and failed startup."""
        for name in list(self.services.list_services().keys()):
            try:
                self.services.unregister_service(name)
            except Exception:
                logger.warning("Failed to unregister service '%s'", name, exc_info=True)
