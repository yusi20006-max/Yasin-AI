# Security & Supply-chain Hardening

**Platform:** Yasin-AI 1.1.4  
**Status:** Implemented baseline (not a formal third-party audit)

## CI security gates (blocking)

| Gate | Location | Purpose |
|---|---|---|
| `pip-audit` | `.github/workflows/ci.yml` → `security` job | Dependency vulnerability scan |
| Repository security check | `yasin security check` | Secrets, crypto, policy files |
| Forbidden secret files | CI bash step | Blocks committed `.env`/key material |
| Ruff lint | `lint` job | Static quality gate |
| Coverage floor | pytest `--cov-fail-under=85` | Regression safety |

## Runtime security baseline

- Credentials only via environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, …)
- Provider exception messages redact raw HTTP bodies
- API 500 responses never leak exception text
- Plugin registry defaults to trusted in-process plugins only
- Docker production profile: non-root, `cap_drop: ALL`, `no-new-privileges`

## Explicit non-claims

- No formal penetration test certificate
- No claim of complete vulnerability absence
- Untrusted plugin sandbox is **not** implemented (see #143)

## Verification

```bash
python -m pytest tests/test_security_supply_chain.py -q
python -c "from yasinai.cli.security_entrypoint import main; main()" security check
```
