"""Local credential registry owned by Yasin-AI.

Credentials are persisted only by the registry, never returned by its public
listing API. Files are created with owner-only permissions and replaced
atomically.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any


class CredentialRegistryError(RuntimeError):
    """Raised when credential registry persistence fails."""


class CredentialRegistry:
    def __init__(self, path: str | Path | None = None) -> None:
        configured = path or os.environ.get("YASINAI_CREDENTIAL_REGISTRY")
        self.path = Path(configured) if configured else (
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "yasinai" / "credentials.json"
        )
        self._lock = RLock()

    @staticmethod
    def credential_id(provider: str, credential: str) -> str:
        digest = hashlib.sha256(f"{provider}\0{credential}".encode("utf-8")).hexdigest()
        return f"cred_{digest[:24]}"

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "credentials": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CredentialRegistryError("credential registry is unreadable") from exc
        if not isinstance(data, dict) or not isinstance(data.get("credentials", {}), dict):
            raise CredentialRegistryError("credential registry has invalid structure")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.path.parent, 0o700)
        fd, tmp = tempfile.mkstemp(prefix=".credentials-", dir=str(self.path.parent), text=True)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, self.path)
            os.chmod(self.path, 0o600)
        except OSError as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise CredentialRegistryError("credential registry could not be written") from exc

    def import_credential(
        self,
        *,
        provider: str,
        credential: str,
        model: str | None = None,
        label: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], bool]:
        provider = provider.strip().lower()
        if not provider or not credential:
            raise ValueError("provider and credential are required")
        credential_id = self.credential_id(provider, credential)
        record = {
            "id": credential_id,
            "provider": provider,
            "model": model,
            "label": label,
            "metadata": dict(metadata or {}),
            "credential": credential,
        }
        with self._lock:
            data = self._read()
            existing = data["credentials"].get(credential_id)
            if existing:
                return self._public_record(existing), False
            data["credentials"][credential_id] = record
            self._write(data)
            return self._public_record(record), True

    def get_credential(self, credential_id: str) -> str | None:
        with self._lock:
            record = self._read()["credentials"].get(credential_id)
            return record.get("credential") if isinstance(record, dict) else None

    def list_public(self) -> list[dict[str, Any]]:
        with self._lock:
            data = self._read()
            return [self._public_record(record) for record in data["credentials"].values()]

    @staticmethod
    def _public_record(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": record.get("id"),
            "provider": record.get("provider"),
            "model": record.get("model"),
            "label": record.get("label"),
            "metadata": dict(record.get("metadata") or {}),
        }
