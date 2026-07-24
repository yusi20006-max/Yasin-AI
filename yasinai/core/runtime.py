"""Lifecycle Orchestrator for YasinAI Core Runtime."""

import logging
from typing import Optional
from yasinai.core.config import Configuration, load_config
from yasinai.core.system import SystemRegistry, SystemInfo
from yasinai.core.bootstrap import BootstrapManager

logger = logging.getLogger("yasinai.core.runtime")


class RuntimeOrchestrator:
    """Orchestrates YasinAI lifecycle from startup to shutdown."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize orchestrator components."""
        self.config: Configuration = load_config(config_path)
        self.registry: SystemRegistry = SystemRegistry()
        self.system_info: SystemInfo = SystemInfo()
        self.bootstrap_manager: BootstrapManager = BootstrapManager(self.registry)
        self.state: str = "STOPPED"

        # Register core system services
        self.registry.register("config", self.config)
        self.registry.register("system_info", self.system_info)

    def startup(self) -> None:
        """Orchestrate system startup.

        Flow: Startup -> Bootstrap -> Runtime Initialization -> Module Registration -> System Ready
        """
        logger.info("Initializing Startup...")
        self.state = "STARTING"

        # 1. Bootstrap Phase
        logger.info("Starting Bootstrap manager...")
        self.state = "BOOTSTRAP"

        # 2. Runtime Initialization Phase
        logger.info("Initializing runtime services...")
        self.state = "INITIALIZING"

        # 3. Module Registration Phase
        logger.info("Registering system modules...")
        self.state = "REGISTERING"

        # 4. System Ready Phase
        logger.info("YasinAI Core Runtime is now ready.")
        self.state = "READY"

    def shutdown(self) -> None:
        """Orchestrate system shutdown."""
        logger.info("Initiating system shutdown...")
        self.state = "SHUTTING_DOWN"

        # Clear/Unregister services
        for name in list(self.registry.list_services().keys()):
            self.registry.unregister(name)

        self.state = "STOPPED"
        logger.info("YasinAI Core Runtime stopped.")
