from __future__ import annotations

import importlib.metadata
import logging
import os
import platform
import subprocess
import sys
from typing import Any, Optional

logger = logging.getLogger(__name__)


def detect_android_api_level() -> Optional[int]:
    """Detect Android API level if running under Android/Termux."""
    if hasattr(sys, "getandroidapilevel"):
        try:
            return sys.getandroidapilevel()  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            logger.debug("sys.getandroidapilevel() call failed")

    for key in ("ANDROID_API_LEVEL", "RO_BUILD_VERSION_SDK"):
        val = os.environ.get(key)
        if val and val.isdigit():
            return int(val)

    try:
        res = subprocess.run(
            ["getprop", "ro.build.version.sdk"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip().isdigit():
            return int(res.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        logger.debug("Failed to detect Android API level via getprop")

    return None


def detect_termux() -> bool:
    """Check whether execution is inside a Termux environment."""
    if os.environ.get("TERMUX_VERSION"):
        return True
    return os.path.exists("/data/data/com.termux")


def detect_native_deps() -> dict[str, Optional[str]]:
    """Gather native dependency version diagnostics."""
    crypto_ver: Optional[str] = None
    cffi_ver: Optional[str] = None
    openssl_ver: Optional[str] = None

    try:
        crypto_ver = importlib.metadata.version("cryptography")
    except importlib.metadata.PackageNotFoundError:
        try:
            import cryptography
            crypto_ver = getattr(cryptography, "__version__", None)
        except ImportError:
            logger.debug("cryptography package is not installed")

    try:
        cffi_ver = importlib.metadata.version("cffi")
    except importlib.metadata.PackageNotFoundError:
        try:
            import cffi
            cffi_ver = getattr(cffi, "__version__", None)
        except ImportError:
            logger.debug("cffi package is not installed")

    try:
        import ssl
        openssl_ver = getattr(ssl, "OPENSSL_VERSION", None)
    except ImportError:
        logger.debug("ssl module is not available")

    return {
        "cryptography_version": crypto_ver,
        "cffi_version": cffi_ver,
        "openssl_version": openssl_ver,
    }


class SystemInfo:
    """
    Provides key information about the running YasinAI system and its environment.
    """

    def __init__(self, app_name: str = "YasinAI", version: str = "1.1.4", status: str = "unknown") -> None:
        self.app_name: str = app_name
        self.version: str = version
        self.status: str = status

    def get_info(self) -> dict[str, Any]:
        """
        Get system and environment details.
        """
        try:
            deps = detect_native_deps()
            return {
                "app_name": self.app_name,
                "version": self.version,
                "status": self.status,
                "python_version": sys.version,
                "platform": platform.platform(),
                "os": platform.system(),
                "architecture": platform.machine(),
                "is_termux": detect_termux(),
                "android_api_level": detect_android_api_level(),
                "cryptography_version": deps["cryptography_version"],
                "cffi_version": deps["cffi_version"],
                "openssl_version": deps["openssl_version"],
            }
        except Exception:
            logger.exception("Failed to gather system information")
            # Return basic fallback information to ensure non-breaking behavior
            return {
                "app_name": self.app_name,
                "version": self.version,
                "status": self.status,
                "python_version": sys.version,
                "platform": "Unknown",
                "os": "Unknown",
                "architecture": "Unknown",
                "is_termux": False,
                "android_api_level": None,
                "cryptography_version": None,
                "cffi_version": None,
                "openssl_version": None,
            }


class ServiceRegistry:
    """
    A service registry to register and manage core services within the runtime.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register_service(self, name: str, service: Any, overwrite: bool = False) -> None:
        """
        Register a service with a unique name.
        """
        if name in self._services and not overwrite:
            msg = f"Service '{name}' is already registered. Use overwrite=True to replace it."
            logger.error(msg)
            raise ValueError(msg)
        self._services[name] = service
        logger.debug(f"Service '{name}' successfully registered.")

    def get_service(self, name: str) -> Any:
        """
        Retrieve a registered service by its name.
        """
        if name not in self._services:
            msg = f"Service '{name}' not found in the registry."
            logger.error(msg)
            raise KeyError(msg)
        return self._services[name]

    def has_service(self, name: str) -> bool:
        """
        Check if a service is registered.
        """
        return name in self._services

    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service from the registry.
        """
        if name in self._services:
            del self._services[name]
            logger.debug(f"Service '{name}' unregistered successfully.")
            return True
        logger.warning(f"Attempted to unregister non-existent service: '{name}'")
        return False

    def list_services(self) -> dict[str, Any]:
        """
        Return all registered services.
        """
        return self._services.copy()
