"""
Generation Capability Contract v1

Stable interface for text/chat generation.
Backed by yasinai.services.GenerationService → ProviderRouter.
Consumers must not import yasinai.providers directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from yasinai.contracts.base import (
    CapabilityMetadata,
    ContractViolationError,
    ObservabilityContext,
)


@dataclass(frozen=True)
class GenerationRequest:
    """
    Input contract for text generation.

    Attributes:
        prompt:          User prompt (required, non-empty)
        model:           Optional model hint for routing
        max_tokens:      Max tokens to generate (default 1024)
        temperature:     Sampling temperature 0.0–2.0 (default 0.7)
        system_prompt:   Optional system instruction
        stop_sequences:  Optional stop strings
        provider:        Optional preferred provider name (e.g. openai, local)
        metadata:        Caller-supplied context
        context:         Observability tracing context
    """

    prompt: str
    model: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    stop_sequences: List[str] = field(default_factory=list)
    provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ObservabilityContext] = None

    MAX_TOKENS_LIMIT = 32000

    def __post_init__(self) -> None:
        if not self.prompt or not str(self.prompt).strip():
            raise ContractViolationError("GenerationRequest: 'prompt' must not be empty")
        if not 0.0 <= self.temperature <= 2.0:
            raise ContractViolationError(
                "GenerationRequest: 'temperature' must be between 0.0 and 2.0"
            )
        if self.max_tokens < 1:
            raise ContractViolationError("GenerationRequest: 'max_tokens' must be >= 1")
        if self.max_tokens > self.MAX_TOKENS_LIMIT:
            raise ContractViolationError(
                f"GenerationRequest: 'max_tokens' must be <= {self.MAX_TOKENS_LIMIT}"
            )


@dataclass(frozen=True)
class GenerationResult:
    """
    Output contract for a generation call.

    Attributes:
        success:        True if generation completed without error
        text:           Generated text (empty on failure)
        model:          Model id that produced the text
        provider:       Provider name that handled the request
        input_tokens:   Estimated/reported input tokens
        output_tokens:  Estimated/reported output tokens
        finish_reason:  Provider finish reason if available
        error:          Error message if success is False
        meta:           Capability metadata
    """

    success: bool
    text: str = ""
    model: Optional[str] = None
    provider: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: Optional[str] = None
    error: Optional[str] = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="generation")
    )
