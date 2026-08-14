# Yasin-AI v1.1.0 Production Release

Release target: `v1.1.0`

## Gate status

- Security audit completed for both `v1.0.0` and the post-release maintenance `v1.1.0` branch.
- Release-candidate checklist completed.
- CI test, coverage, dependency-audit, repository-security, and Docker smoke-test gates are defined and fully passing.
- Packaging metadata reports version `1.1.0` in `pyproject.toml` and runtime reports `1.1.0` in `yasinai/__init__.py`.
- Production deployment hardening is documented.
- Known limitations are documented and intentionally accepted for this release.

## Deployment verification

Before exposing a deployment to users, run:

```bash
python -m pytest -q
pip-audit
python -m build
```

Then build and exercise the production container/compose profile in the target environment and verify its healthcheck.

## Rollback

Keep the previous known-good image/package available. If a production deployment fails health checks or introduces a regression, redeploy the previous artifact and investigate from the release commit and CI artifacts.

## Scope

This release establishes the current stable production maintenance baseline of the modular YasinAI platform (`v1.1.0`). Distributed HA storage, untrusted plugin sandboxing, and vendor-specific observability exporters remain future infrastructure work.

---

## Phase 5.1 — Production profile verification (2026-08-14)

Automated static gates live in `tests/test_production_profile.py`:

| Gate | Check |
|---|---|
| Non-root image | Dockerfile `USER 10001` + `useradd` |
| Image health | Dockerfile `HEALTHCHECK` → `yasin status` |
| No secret bake-in | Dockerfile does not `COPY .env` |
| Production compose | `read_only`, `cap_drop: ALL`, `no-new-privileges`, limits, volume |
| Secret hygiene | `.env.example` present; `.gitignore` blocks `.env` / keys |

Operators still must run the production compose profile in the target environment
before exposing traffic:

```bash
docker compose -f deploy/compose.production.yml up --build -d
docker compose -f deploy/compose.production.yml ps
```

---

## Phase 5.3 — Production readiness gate (2026-08-14)

Automated readiness module: `tests/test_production_readiness.py`

Validates:

1. Version alignment (`pyproject.toml` / `yasinai.__version__` = 1.1.0)
2. Phase 3 modules (providers, generation, RAG)
3. Phase 4 integration clients (Agent, Hub, CLI, Relay, Feed, Press)
4. Phase 5 hardening artifacts (plugin trust policy, production profile tests)
5. CI gates (`cov-fail-under`, pip-audit, security check)
6. Public import smoke (contracts, services, integration, providers)

`RELEASE_CHECKLIST.md` sections 12–14 record Phase 3–5 completion for the
v1.1.0 maintenance line.
