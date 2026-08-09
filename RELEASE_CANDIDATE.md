# Yasin-AI Release Candidate

## RC checklist

- [x] Security policy and final audit recorded
- [x] Dependency audit gate configured
- [x] CI test and coverage gates configured
- [x] Canonical Python packaging
- [x] Runtime lifecycle hardening
- [x] Persistent memory and semantic storage
- [x] Developer plugin SDK
- [x] Transport-neutral service layer
- [x] Observability primitives
- [x] Hardened container deployment baseline
- [x] Architecture documentation
- [x] Performance/reliability regression coverage

## Release policy

The release candidate is cut from `main` after the Phase 15 security hardening. No release is considered production-ready until CI, dependency auditing, and the final security checklist pass on the exact release commit.

## Known limitations

Plugin execution is trusted and in-process. External/untrusted plugin execution requires a sandbox and authorization layer and is not part of this release candidate.

The application currently uses local SQLite-backed persistence. HA/distributed storage is not claimed by this release candidate.

## Verification commands

```bash
python -m pytest -q
pip-audit
python -m build
```

Container verification should additionally run the production compose profile and its healthcheck in the deployment environment.
