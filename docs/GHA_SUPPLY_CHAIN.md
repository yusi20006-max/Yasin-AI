# GitHub Actions Supply-chain Hardening

**Status:** Implemented for Yasin-AI CI

## Controls

| Control | Status |
|---|---|
| `permissions: contents: read` default | Yes |
| Action majors pinned (`checkout@v7`, `setup-python@v5`, `upload-artifact@v5`) | Yes |
| `persist-credentials: false` on checkout | Yes |
| Concurrency groups with cancel-in-progress | Yes |
| No third-party actions beyond official `actions/*` | Yes |
| Security job blocking (pip-audit + repo scan) | Yes |

## Non-claims

- Actions are pinned to **major** tags, not commit SHAs (accepted operational trade-off).
- No self-hosted runners in this repository.

## Verification

`tests/test_gha_supply_chain.py`
