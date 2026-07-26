import logging
from typing import Any, Dict, Optional
from yasinai.core.config import Config
from yasinai.core.system import SystemInfo, ServiceRegistry
from yasinai.core.bootstrap import Bootstrap

logger = logging.getLogger(__name__)


class Runtime:
    """
    The central execution engine of YasinAI, managing lifecycle and services.
    """

    def __init__(self, config_defaults: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Core Runtime with configuration, services, and system info.
        """
        self.config: Config = Config(defaults=config_defaults)
        self.services: ServiceRegistry = ServiceRegistry()

        self.system_info: SystemInfo = SystemInfo(
            app_name=self.config.get("app_name", "YasinAI"),
            version=self.config.get("version", "1.0.0"),
            status="inactive"
        )

        self.bootstrap_loader: Bootstrap = Bootstrap(self)
        self.state: str = "STOPPED"

    def start(self) -> None:
        """
        Orchestrate the entire runtime startup flow:
        Startup -> Bootstrap -> Runtime Initialization -> Module Registration -> System Ready
        """
        logger.info("Starting Core Runtime orchestration flow...")
        self.startup()
        self.bootstrap()
        self.initialize()
        self.register_modules()
        self.ready()
        logger.info("Core Runtime successfully started and ready.")

    def startup(self) -> None:
        """
        Phase 1: Startup
        Initializes the startup phase and registers basic configuration and system services.
        """
        logger.info("Runtime phase: STARTUP")
        self.state = "STARTING"
        self.system_info.status = "starting"
        self.services.register_service("config", self.config, overwrite=True)
        self.services.register_service("system_info", self.system_info, overwrite=True)

    def bootstrap(self) -> None:
        """
        Phase 2: Bootstrap
        Discovers and dynamically imports configured modules and extensions.
        """
        logger.info("Runtime phase: BOOTSTRAP")
        if self.state != "STARTING":
            logger.error(f"Cannot bootstrap from state: {self.state}")
            raise RuntimeError(f"Cannot bootstrap from state: {self.state}")

        self.state = "BOOTSTRAPPING"
        module_names = self.config.get("modules", [])
        self.bootstrap_loader.discover_and_load(module_names)

    def initialize(self) -> None:
        """
        Phase 3: Runtime Initialization
        Performs essential core systems and state setup.
        """
        logger.info("Runtime phase: INITIALIZATION")
        if self.state != "BOOTSTRAPPING":
            logger.error(f"Cannot initialize from state: {self.state}")
            raise RuntimeError(f"Cannot initialize from state: {self.state}")

        self.state = "INITIALIZING"

    def register_modules(self) -> None:
        """
        Phase 4: Module Registration
        Registers active modules and custom application features.
        """
        logger.info("Runtime phase: REGISTER_MODULES")
        if self.state != "INITIALIZING":
            logger.error(f"Cannot register modules from state: {self.state}")
            raise RuntimeError(f"Cannot register modules from state: {self.state}")

        self.state = "REGISTERING_MODULES"

    def ready(self) -> None:
        """
        Phase 5: System Ready
        Transitions system status to ready, making YasinAI operational.
        """
        logger.info("Runtime phase: READY")
        if self.state != "REGISTERING_MODULES":
            logger.error(f"Cannot set ready from state: {self.state}")
            raise RuntimeError(f"Cannot set ready from state: {self.state}")

        self.state = "READY"
        self.system_info.status = "ready"
        self.services.register_service("runtime", self, overwrite=True)

    def shutdown(self) -> None:
        """
        Shutdown sequence: Gracefully stops the runtime and all services.
        """
        logger.info("Initiating Runtime shutdown sequence...")
        self.state = "SHUTTING_DOWN"
        self.system_info.status = "shutdown"

        for name in list(self.services.list_services().keys()):
            self.services.unregister_service(name)

        self.state = "STOPPED"
        logger.info("Runtime gracefully stopped.")
