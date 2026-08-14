# Yasin-Agent ↔ Yasin-AI Integration

**Phase:** 4.1  
**Status:** Reference client available  
**Date:** 2026-08-14

---

## Ownership boundary

| Platform | Owns |
|---|---|
| **Yasin-Agent** | Agent planning, workflows, tool loops, multi-step orchestration |
| **Yasin-AI** | Canonical AI capabilities: memory, knowledge/retrieval, generation, RAG |

Yasin-Agent **must not** import:

- `knowledge_platform`
- `developer_platform`
- `yasinai.providers.*` (except if Agent is embedding a local runtime — prefer services)
- Any provider SDK (`openai`, `anthropic`, …)

Yasin-Agent **must** import from:

```python
from yasinai.contracts import (
    MemoryRequest, KnowledgeQuery, GenerationRequest, RagRequest, ...
)
from yasinai.services import KnowledgeService, GenerationService, RagService
# or the reference client:
from yasinai.integration import YasinAgentClient
```

---

## Recommended client

```python
from yasinai.integration import YasinAgentClient

client = YasinAgentClient()

client.remember("user prefers short answers")
client.index_document("doc1", "Yasin-AI is the canonical AI platform.")
result = client.answer("What is Yasin-AI?", include_memory=True)
assert result.success
print(result.answer)
```

### Capability map

| Agent need | Yasin-AI API |
|---|---|
| Session memory | `client.remember` / `client.recall` |
| Index knowledge | `client.index_document` |
| Semantic search | `client.search` |
| Direct generation | `client.generate` |
| Grounded answers | `client.answer` (RAG) |

---

## Credentials

Provider keys remain process environment variables on the host that runs
Yasin-AI services (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). Yasin-Agent never
embeds keys in prompts or source.

Without cloud keys, `LocalProvider` remains available for offline/dev paths.

---

## Tests

See `tests/test_integration_agent.py` for boundary smoke tests.
