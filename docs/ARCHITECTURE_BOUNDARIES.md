# Architecture Boundaries

**Platform:** Yasin-AI 1.1.4

## Layer diagram

```
Consumers (Agent / Hub / CLI / …)
        │  only public imports
        ▼
 yasinai.contracts  +  yasinai.services  +  yasinai.integration
        │
        ▼
 yasinai.providers / yasinai.core
        │
        ▼
 knowledge_platform / developer_platform / security_platform   (PRIVATE)
```

## Allowed dependencies

| From | May import |
|---|---|
| `yasinai.contracts` | stdlib, `yasinai.contracts.*` only |
| `yasinai.integration` | `yasinai.contracts`, `yasinai.services` |
| `yasinai.services` | contracts, providers, private platforms (facade) |
| `yasinai.providers` | providers package, stdlib (no private platforms) |
| Private platforms | each other + stdlib (not contracts required) |

## Forbidden

- Consumers importing private platforms
- `yasinai.contracts` importing services/providers/platforms
- Provider adapters importing `knowledge_platform` / `developer_platform`

## Verification

`tests/test_architecture_boundaries.py`
