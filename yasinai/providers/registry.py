"""
Provider Registry — single registry per Runtime instance.

Providers register themselves by name; the registry does NOT import
any provider SDK. Each provider adapter self-registers on import.

Phase 2.6: registry skeleton defined.
Phase 3: concrete providers register here.
"""
from __future__ import annotations

import logging
from threading import Lock
from typing import Dict, List, Optional

from yasinai.providers.base import ProviderBase, ProviderCapability, ProviderInfo

logger = logging.getLogger(__name__)


class ProviderRegistryError(Exception):
    pass


class ProviderRegistry:
    """Thread-safe registry of provider adapters."""

    def __init__(self) -> None:
        self._providers: Dict[str, ProviderBase] = {}
        self._lock = Lock()

    def register(self, provider: ProviderBase, *, overwrite: bool = False) -> None:
        name = provider.info.name
        with self._lock:
            if name in self._providers and not overwrite:
                raise ProviderRegistryError(
                    f"Provider '{name}' is already registered. "
                    "Use overwrite=True to replace it."
                )
            self._providers[name] = provider
            logger.info("Provider registered: %s (capabilities: %s)", name,
                        [c.value for c in provider.info.capabilities])

    def unregister(self, name: str) -> bool:
        with self._lock:
            existed = name in self._providers
            self._providers.pop(name, None)
            return existed

    def get(self, name: str) -> Optional[ProviderBase]:
        with self._lock:
            return self._providers.get(name)

    def list(self) -> List[ProviderInfo]:
        with self._lock:
            return [p.info for p in self._providers.values()]

    def for_capability(self, capability: ProviderCapability) -> List[ProviderBase]:
        """Return all providers that support a given capability."""
        with self._lock:
            return [
                p for p in self._providers.values()
                if capability in p.info.capabilities
            ]

    def available_for_capability(self, capability: ProviderCapability) -> List[ProviderBase]:
        """Return providers that support the capability AND report is_available()."""
        return [p for p in self.for_capability(capability) if p.is_available()]

    def __len__(self) -> int:
        with self._lock:
            return len(self._providers)
