"""
LocalProvider — offline generation adapter (no network, no external SDK).

Always available. Useful for tests, CI, and air-gapped environments.
"""
from __future__ import annotations

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderInfo,
)


class LocalProvider(ProviderBase):
    """Deterministic local stub that echoes structured completions."""

    DEFAULT_MODEL = "local-echo-v1"

    def __init__(self, *, model_id: str | None = None) -> None:
        self._model_id = model_id or self.DEFAULT_MODEL

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="local",
            version="1.0.0",
            capabilities=[
                ProviderCapability.GENERATION,
                ProviderCapability.CHAT,
            ],
            model_ids=[self._model_id],
            metadata={"network": False, "sdk": None},
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        model = request.model or self._model_id
        system = request.system_prompt or ""
        prefix = f"[system: {system}] " if system else ""
        text = (
            f"{prefix}[local:{model}] "
            f"{request.prompt[: max(1, request.max_tokens)]}"
        )
        if request.stop_sequences:
            for stop in request.stop_sequences:
                if stop and stop in text:
                    text = text.split(stop, 1)[0]
                    break
        # Rough token estimate: ~4 chars per token
        in_tok = max(1, len(request.prompt) // 4)
        out_tok = max(1, len(text) // 4)
        return GenerationResponse(
            text=text,
            model=model,
            provider="local",
            input_tokens=in_tok,
            output_tokens=out_tok,
            metadata={"temperature": request.temperature},
        )
