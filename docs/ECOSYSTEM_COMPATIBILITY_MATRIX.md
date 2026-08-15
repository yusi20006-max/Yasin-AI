# Yasin Ecosystem Version Compatibility Matrix

**Yasin-AI platform version:** 1.1.4  
**Public API contract:** v1  
**Last updated:** 2026-08-16

## Policy

- Yasin-AI follows SemVer. Within `1.1.x`, public contracts (`CONTRACT_VERSION = "v1"`) remain backward-compatible.
- Ecosystem consumers must depend on **public** packages only (`yasinai.contracts`, `yasinai.services`, `yasinai.providers`, `yasinai.integration`, `yasinai.core.runtime` / `config`).
- Private packages (`knowledge_platform`, `developer_platform`, `security_platform`) are **not** part of the compatibility surface.

## Supported ranges (Yasin-AI 1.1.4)

| Consumer | Minimum Yasin-AI | Maximum Yasin-AI (inclusive) | Contract | Notes |
|---|---|---|---|---|
| Yasin-Agent | `>=1.1.4` | `<1.2.0` | v1 | Use `yasinai.integration.YasinAgentClient` or contracts/services directly |
| Yasin-Core | `>=1.1.4` | `<1.2.0` | v1 | Runtime + Config public API |
| Yasin-CLI | `>=1.1.4` | `<1.2.0` | v1 | Local `yasin` CLI + `YasinCLIClient` |

## Machine-readable matrix

See `yasinai/compatibility.py` — imported by `tests/test_compatibility_matrix.py` and usable by CI.

## Verification

```bash
python -m pytest tests/test_compatibility_matrix.py -q
```
