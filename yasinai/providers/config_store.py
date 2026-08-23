"""Persistent configuration for runtime-defined providers.

Provider metadata is stored as JSON, while API keys are encrypted with the
existing Yasin-AI AES-256-GCM engine.  The encryption master key is accepted
only from ``YASINAI_MASTER_KEY`` and is never written by this module.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from security_platform.encryption import EncryptionEngine


class ProviderConfigError(ValueError):
    """Raised when provider configuration is invalid or unavailable."""


def validate_base_url(base_url: str) -> str:
    """Validate and normalize a provider API base URL."""
    value = base_url.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ProviderConfigError("Base URL must be a valid HTTP(S) URL")
    host = (parsed.hostname or "").lower()
    local = host in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not local:
        raise ProviderConfigError("Remote provider Base URL must use HTTPS")
    if parsed.username or parsed.password:
        raise ProviderConfigError("Base URL must not contain embedded credentials")
    return value


def _default_path() -> Path:
    return Path(os.environ.get("YASINAI_PROVIDER_CONFIG", "~/.config/yasinai/providers.json")).expanduser()


def _master_key() -> str:
    key = os.environ.get("YASINAI_MASTER_KEY")
    if not key:
        raise ProviderConfigError("Set YASINAI_MASTER_KEY before configuring providers")
    return key


class ProviderStore:
    """Encrypted on-disk store for user-defined provider profiles."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _default_path()
        self.engine = EncryptionEngine()

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"providers": {}, "default": None}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProviderConfigError("Provider configuration cannot be read") from exc
        if not isinstance(data, dict) or not isinstance(data.get("providers", {}), dict):
            raise ProviderConfigError("Provider configuration is invalid")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def list(self) -> list[dict[str, Any]]:
        data = self._read()
        return [
            {
                "name": name,
                "base_url": item["base_url"],
                "model": item["model"],
                "default": name == data.get("default"),
            }
            for name, item in data["providers"].items()
        ]

    def get(self, name: str) -> dict[str, str] | None:
        item = self._read()["providers"].get(name)
        if item is None:
            return None
        try:
            key = self.engine.decrypt(item["api_key_encrypted"], _master_key())
        except (KeyError, ValueError) as exc:
            raise ProviderConfigError("Stored provider credentials cannot be decrypted") from exc
        return {
            "name": name,
            "base_url": item["base_url"],
            "model": item["model"],
            "api_key": key,
        }

    def save(self, *, name: str, base_url: str, model: str, api_key: str, make_default: bool = False) -> None:
        name = name.strip()
        model = model.strip()
        if not name:
            raise ProviderConfigError("Provider name must not be empty")
        if not model:
            raise ProviderConfigError("Model must not be empty")
        if not api_key:
            raise ProviderConfigError("API key must not be empty")
        normalized = validate_base_url(base_url)
        data = self._read()
        data["providers"][name] = {
            "base_url": normalized,
            "model": model,
            "api_key_encrypted": self.engine.encrypt(api_key, _master_key()),
        }
        if make_default or not data.get("default"):
            data["default"] = name
        self._write(data)

    def remove(self, name: str) -> bool:
        data = self._read()
        if name not in data["providers"]:
            return False
        del data["providers"][name]
        if data.get("default") == name:
            data["default"] = next(iter(data["providers"]), None)
        self._write(data)
        return True

    def use(self, name: str) -> None:
        data = self._read()
        if name not in data["providers"]:
            raise ProviderConfigError(f"Provider '{name}' is not configured")
        data["default"] = name
        self._write(data)

    def default(self) -> dict[str, str] | None:
        data = self._read()
        name = data.get("default")
        return self.get(name) if name else None
