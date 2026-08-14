# Yasin-AI — Provider Architecture

**Phase:** 2.6  
**Status:** Phase 3.1 complete — OpenAI, Anthropic, Local adapters implemented.  
**Date:** 2026-08-14

---

## Boundary Rule

Provider SDK libraries (openai, anthropic, etc.) must **never** be imported
outside `yasinai/providers/`. The rest of Yasin-AI depends only on:

```
yasinai.providers.base    — ProviderBase, GenerationRequest/Response, ProviderCapability
yasinai.providers.registry — ProviderRegistry
yasinai.providers.router   — ProviderRouter
```

Public contracts (`yasinai.contracts`) are separate and provider-neutral.
Consumer projects import from `yasinai.contracts`, not from `yasinai.providers`.

---

## Architecture

```
Consumer (Yasin-Agent, YasinRelay, ...)
        │
        ▼
yasinai.contracts (GenerationRequest — public, provider-neutral)
        │
        ▼
Yasin-AI service layer (Phase 3)
        │
        ▼
ProviderRouter.select(capability, model_hint)
        │
        ▼
ProviderRegistry — available providers
        │
        ├── OpenAIProvider   (Phase 3)
        ├── AnthropicProvider (Phase 3)
        ├── LocalProvider    (Phase 3)
        └── ...
```

---

## Components

### ProviderBase (`yasinai/providers/base.py`)
Abstract interface every provider adapter implements.

- `info → ProviderInfo` — name, version, capabilities, model_ids
- `is_available() → bool` — runtime health check (no I/O in this call)
- `generate(GenerationRequest) → GenerationResponse`
- `ProviderError` — only exception type that may escape an adapter

### ProviderRegistry (`yasinai/providers/registry.py`)
Thread-safe in-process registry. One per Runtime instance.

- `register(provider, overwrite=False)`
- `get(name) → Optional[ProviderBase]`
- `for_capability(cap) → List[ProviderBase]`
- `available_for_capability(cap) → List[ProviderBase]`

### ProviderRouter (`yasinai/providers/router.py`)
Selects the best available provider for a capability + optional model hint.

**Phase 2.6 routing policy (simple):**
1. Filter to providers supporting the capability and `is_available()`.
2. If `model` hint given, prefer provider whose `model_ids` contains it.
3. Otherwise first available wins.
4. If none: `ProviderUnavailableError`.

**Phase 3 extensions (not yet):** priority weights, cost routing, fallback chains, config-driven.

---

## Credential Policy

- Provider credentials (API keys) are **never** stored in source or config files.
- Adapters read credentials from environment variables only.
- Credential names will be documented per-adapter in Phase 3.
- `is_available()` must not block or make network calls — it checks env vars only.

---

## Adding a Provider (Phase 3 guide)

```python
# yasinai/providers/openai_provider.py

import os
from yasinai.providers.base import (
    ProviderBase, ProviderCapability, ProviderError,
    ProviderInfo, GenerationRequest, GenerationResponse,
)

class OpenAIProvider(ProviderBase):

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openai",
            version="1.0.0",
            capabilities=[
                ProviderCapability.GENERATION,
                ProviderCapability.CHAT,
                ProviderCapability.EMBEDDING,
            ],
            model_ids=["gpt-4o", "gpt-4o-mini", "text-embedding-3-small"],
        )

    def is_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        try:
            import openai  # imported here, not at module level
            ...
        except Exception as exc:
            raise ProviderError("openai", str(exc), retryable=True) from exc
```

Register at runtime startup:
```python
from yasinai.providers import ProviderRegistry
from yasinai.providers.openai_provider import OpenAIProvider

registry = ProviderRegistry()
registry.register(OpenAIProvider())
```

---

## Phase 2.6 Audit Findings

| Item | Finding |
|---|---|
| Provider SDK imports | None exist in codebase — clean boundary |
| Provider dependencies in pyproject.toml | None — correct for Phase 2 |
| Provider leakage into contracts | None — contracts are provider-neutral |
| Model routing | Skeleton implemented, Phase 3 for production policy |
| Credential handling | No hardcoded secrets found |
| Retry/fallback | Defined as ProviderRouter responsibility — Phase 3 |

---

*Related: `AI_CAPABILITY_CATALOG.md`, `docs/CAPABILITY_CONTRACTS_V1.md`, ADR-0007*
