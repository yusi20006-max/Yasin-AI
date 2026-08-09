# Yasin-AI v1.0.0 Production Release

Release target: `v1.0.0`

## Gate status

- Security audit completed.
- Release-candidate checklist completed.
- CI test, coverage, dependency-audit, repository-security, and Docker smoke-test gates are defined.
- Packaging metadata reports version `1.0.0`.
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

This release establishes the first production baseline of the modular YasinAI platform. Distributed HA storage, untrusted plugin sandboxing, and vendor-specific observability exporters remain future infrastructure work.
