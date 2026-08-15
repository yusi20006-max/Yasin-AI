"""
Yasin-AI Provider Base Interface

All provider adapters (OpenAI, Anthropic, local models, etc.) must
implement ProviderBase. This is the only interface the rest of Yasin-AI
depends on — never import provider SDK libraries outside this package.

Phase 2.6: interface defined.
Phase 3: concrete implementations added here as submodules.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderCapability(str, Enum):
    """Capabilities a provider may or may not support."""
    GENERATION = "generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    VISION = "vision"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    STRUCTURED_OUTPUT = "structured_output"
    FUNCTION_CALLING = "function_calling"


@dataclass(frozen=True)
class ProviderInfo:
    """Static metadata about a registered provider."""
    name: str
    version: str = "unknown"
    capabilities: List[ProviderCapability] = field(default_factory=list)
    model_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationRequest:
    """
    Input for text generation.
    Mirrors yasinai.contracts — this internal version may carry
    provider-specific hints that are not part of the public contract.
    """
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    stop_sequences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt:
            raise ValueError("GenerationRequest: 'prompt' must not be empty")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("GenerationRequest: 'temperature' must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            raise ValueError("GenerationRequest: 'max_tokens' must be >= 1")
        if self.max_tokens > 32000:
            raise ValueError("GenerationRequest: 'max_tokens' must be <= 32000")


@dataclass(frozen=True)
class GenerationResponse:
    """Output from a text generation call."""
    text: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProviderBase(ABC):
    """
    Abstract base for all Yasin-AI provider adapters.

    Implementations live in yasinai/providers/<name>.py (Phase 3).
    They must:
      - Not leak provider SDK types outside this package
      - Handle their own retry/rate-limit at the adapter level
      - Raise ProviderError (not SDK exceptions) on failure
    """

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Return static metadata about this provider."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider is reachable and configured."""

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate text. Raises NotImplementedError if GENERATION
        is not in self.info.capabilities.
        """
        if ProviderCapability.GENERATION not in self.info.capabilities:
            raise NotImplementedError(
                f"Provider '{self.info.name}' does not support GENERATION"
            )
        return self._generate(request)

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError


class ProviderError(Exception):
    """
    Raised by provider adapters when a call fails.
    Always use this — never let provider SDK exceptions escape the adapter.
    """
    def __init__(self, provider: str, message: str, retryable: bool = False) -> None:
        super().__init__(f"[{provider}] {message}")
        self.provider = provider
        self.retryable = retryable
