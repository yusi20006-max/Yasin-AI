"""Small immutable response models shared by API transports."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class ServiceResponse:
    status: int
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class HealthResponse:
    status: str
    service: str
    version: str

    def as_dict(self) -> Dict[str, str]:
        return {"status": self.status, "service": self.service, "version": self.version}
