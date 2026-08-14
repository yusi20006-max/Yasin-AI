# YasinCLI ↔ Yasin-AI Integration

**Phase:** 4.3  
**Status:** Reference client + CLI memory path on services  
**Date:** 2026-08-14

---

## Ownership boundary

| Platform | Owns |
|---|---|
| **YasinCLI** | Unified CLI UX (`yasin …` commands) |
| **Yasin-AI** | Capability implementations behind contracts/services |

```python
from yasinai.integration import YasinCLIClient

cli = YasinCLIClient()
cli.seed_demo_documents()
result = cli.search_memory("security", top_k=3)
```

`yasin memory search` now routes through `YasinCLIClient` (not direct
`knowledge_platform` imports).

---

## Capability map

| CLI need | API / command |
|---|---|
| System status | `yasin status` (Runtime) |
| Agent create | `yasin agent create` (Developer Platform SDK) |
| Memory search | `yasin memory search` → `YasinCLIClient.search_memory` |
| Security check | `yasin security check` |
| Programmatic generate/RAG | `YasinCLIClient.generate` / `.answer` |

---

## Tests

`tests/test_cli.py`, `tests/test_integration_cli.py`
