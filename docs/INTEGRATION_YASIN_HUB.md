# YasinHub ↔ Yasin-AI Integration

**Phase:** 4.2  
**Status:** Reference client available  
**Date:** 2026-08-14

---

## Ownership boundary

| Platform | Owns |
|---|---|
| **YasinHub** | Control plane, global observability, fleet health |
| **Yasin-AI** | Canonical AI capabilities + local metrics primitives |

YasinHub must not import `knowledge_platform`, `developer_platform`, or provider SDKs.

```python
from yasinai.integration import YasinHubClient

hub = YasinHubClient()
result = hub.generate("status summary", provider="local")
print(hub.metrics_snapshot())
```

---

## Capability map

| Hub need | API |
|---|---|
| Text generation | `hub.generate(...)` |
| Semantic knowledge query | `hub.query_knowledge(...)` |
| RAG answers | `hub.rag(...)` |
| Telemetry export | `hub.metrics_snapshot()` |

Metrics keys (examples):

- `hub.generation.requests` / `.success` / `.errors`
- `hub.generation.latency`
- `hub.knowledge.requests` / `.success` / `.errors`
- `hub.rag.requests` / `.success` / `.errors` / `.latency`

---

## Tests

See `tests/test_integration_hub.py`.
