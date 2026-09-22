"""Single source of truth for token health state transitions."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from yasinai.providers.validation import ValidationResult

class HealthState(str, Enum):
    UNKNOWN="UNKNOWN"; CHECKING="CHECKING"; HEALTHY="HEALTHY"; PARTIAL="PARTIAL"; FAILED="FAILED"; UNAVAILABLE="UNAVAILABLE"; COOLDOWN="COOLDOWN"; QUARANTINED="QUARANTINED"

@dataclass(frozen=True)
class HealthRecord:
    state: HealthState
    validation: ValidationResult
    retryable: bool = False
    quarantine: bool = False

RETRYABLE_CODES={"RATE_LIMITED","TIMEOUT","NETWORK_ERROR","SERVER_ERROR"}
QUARANTINE_CODES={"INVALID_API_KEY","UNAUTHORIZED","FORBIDDEN"}

class TokenHealthEngine:
    def __init__(self, validator: Callable[[str], ValidationResult]):
        self.validator=validator

    def check(self, credential: str) -> HealthRecord:
        result=self.validator(credential)
        code=result.error_code
        if result.authenticated is True:
            state=HealthState.HEALTHY
        elif result.reachable is False and code in RETRYABLE_CODES:
            state=HealthState.COOLDOWN
        elif code in RETRYABLE_CODES:
            state=HealthState.COOLDOWN
        elif code in QUARANTINE_CODES:
            state=HealthState.QUARANTINED
        elif result.reachable is False:
            state=HealthState.UNAVAILABLE
        elif result.authenticated is False:
            state=HealthState.FAILED
        elif result.authenticated is None and result.reachable is True:
            state=HealthState.PARTIAL
        else:
            state=HealthState.UNKNOWN
        return HealthRecord(state=state, validation=result, retryable=code in RETRYABLE_CODES, quarantine=code in QUARANTINE_CODES)
