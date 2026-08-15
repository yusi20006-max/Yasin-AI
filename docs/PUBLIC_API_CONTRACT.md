# Yasin-AI Public API Contract

**Contract version:** v1  
**Platform version:** 1.1.4  
**Status:** Frozen for ecosystem consumers (Agent, Core, CLI, Hub, Relay, Feed, Press)

This document is the **canonical public surface** of Yasin-AI. Consumers **must** import only symbols and packages listed here. Anything not listed is **private** and may change without notice.

---

## 1. Supported import paths

| Package / module | Public? | Purpose |
|---|---|---|
| `yasinai` | Yes | Package version (`__version__`) |
| `yasinai.contracts` | Yes | Capability request/response contracts |
| `yasinai.services` | Yes | Service facades (generation, knowledge, RAG) |
| `yasinai.providers` | Yes | Provider abstraction, registry, router, concrete adapters |
| `yasinai.providers.base` | Yes | `ProviderBase`, request/response DTOs, errors |
| `yasinai.integration` | Yes | Reference ecosystem clients |
| `yasinai.core.runtime` | Yes | `Runtime` lifecycle |
| `yasinai.core.config` | Yes | `Config` |
| `yasinai.cli` | Yes | Local diagnostic CLI entry (`yasin`) |
| `api_service` | Yes | Transport-neutral API service |
| `observability` | Yes | Metrics primitives (`Counter`, `Timer`, `MetricsRegistry`) |

### Explicitly private (do **not** import from consumers)

| Module / package | Reason |
|---|---|
| `knowledge_platform` | Internal knowledge/memory implementation |
| `developer_platform` | Internal developer/plugin implementation |
| `security_platform` | Internal security implementation (use CLI/`yasin security check`) |
| `yasinai.providers.openai_provider` internals beyond public class export | Prefer `yasinai.providers` |
| Any `_`-prefixed symbol | Private by convention |

---

## 2. Version

```python
import yasinai
assert yasinai.__version__  # e.g. "1.1.4"
```

**Compatibility policy:** Semantic Versioning. Within `1.1.x`, public contracts (`CONTRACT_VERSION = "v1"`) remain backward-compatible. Breaking public API changes require a major package version and a new contract version.

---

## 3. Capability contracts (`yasinai.contracts`)

`CONTRACT_VERSION = "v1"`

### Base
- `CapabilityMetadata`, `ObservabilityContext`
- `CapabilityError`, `CapabilityUnavailableError`, `ContractViolationError`

### Memory
- `MemoryType`, `MemoryRequest`, `MemoryResponse`, `MemoryEntry`

### Knowledge
- `KnowledgeQueryType`, `KnowledgeQuery`, `KnowledgeEntry`, `KnowledgeResult`

### Generation
- `GenerationRequest`, `GenerationResult`

### RAG
- `RagRequest`, `RagResult`

### Embedding
- `EmbeddingRequest`, `EmbeddingResponse`, `EmbeddingVector`

### Plugin
- `PluginContract`, `PluginInvokeRequest`, `PluginInvokeResponse`

---

## 4. Services (`yasinai.services`)

- `KnowledgeService` — memory + knowledge facade
- `GenerationService` — text generation via providers
- `RagService` — retrieval-augmented generation

---

## 5. Providers (`yasinai.providers`)

- `ProviderBase`, `ProviderCapability`, `ProviderInfo`
- `ProviderError`, `ProviderRegistry`, `ProviderRouter`, `ProviderUnavailableError`
- `GenerationRequest`, `GenerationResponse` (provider-layer DTOs)
- `OpenAIProvider`, `AnthropicProvider`, `LocalProvider`
- `build_default_registry`

**Implemented:** explicit provider/model selection, bounded retry/fallback, env-only credentials.  
**Not implemented:** cost-aware / health-aware / load-balanced routing (planned).

---

## 6. Runtime & configuration

- `yasinai.core.runtime.Runtime` — lifecycle (`start` / `shutdown`, states)
- `yasinai.core.config.Config` — defaults + `YASINAI_*` env overrides

---

## 7. Integration clients (`yasinai.integration`)

Reference clients (not required, but supported):

`YasinAgentClient`, `YasinHubClient`, `YasinCLIClient`, `YasinRelayClient`, `YasinFeedClient`, `YasinPressClient`

---

## 8. Error contract (summary)

- Contract validation → `ContractViolationError` (or service result with `success=False`)
- Provider unavailable / model mismatch → `ProviderUnavailableError` / `GenerationResult.success=False`
- Unexpected internals **must not** appear in `GenerationResult.error` / `RagResult.error` / API bodies

Detailed API error schemas: see issue #147 and `api_service` responses.

---

## 9. Verification

Automated: `tests/test_public_api_contract.py` (must pass in CI).

Every symbol listed in the machine-readable registry in that test **must** import successfully.
