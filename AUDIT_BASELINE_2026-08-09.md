# YasinAI Baseline Audit — 2026-08-09

> Immutable project baseline recorded before Phase 1 hardening. This document records the repository state and the verified findings used to drive the next engineering phases.

## Baseline identity

- Repository: `yusi20006-max/Yasin-AI`
- Default branch: `main`
- Baseline branch: `chore/baseline-audit-2026-08-09`
- Baseline `main` HEAD: `0d6f4e2a0134d97faadeffbd994e267302c701f5`
- Baseline `main` tree: `0e43e2066b7b12ac8ac65e5b56dc4b3301dd373b`
- Repository visibility: public
- Repository archived: no
- Current project version declared in `pyproject.toml`: `1.0.0`
- Existing release tag `v1.0.0` points to `9e7e61752455f7b86b1e254612656692dcf28ea3`
- Therefore `main` has advanced beyond the `v1.0.0` tag.

## Repository structure observed

The repository currently contains the core runtime under `yasinai/`, plus `developer_platform/`, `knowledge_platform/`, `security_platform/`, `tests/`, Docker/deployment files, and project documentation including `MASTER_PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`, `PROJECT_STATUS.md`, `RELEASE_CHECKLIST.md`, and release/changelog files.

## CI baseline

The only workflow observed at baseline is `.github/workflows/docker-build.yml`.

It:

1. checks out the repository;
2. appends a temporary `[tool.setuptools]` package list to `pyproject.toml` as a CI workaround;
3. builds the Docker image;
4. runs `yasin status` in the image.

It does not constitute a complete test/security/dependency CI pipeline.

## Packaging baseline

`pyproject.toml` declares setuptools as the build backend and exposes the `yasin` CLI, but it does not declare the project package list. The CI workflow currently compensates by modifying `pyproject.toml` at runtime.

`requirements.txt` contains only `pytest==9.0.2` at baseline.

## Security baseline

### Encryption

`security_platform/encryption.py` implements a custom HMAC-SHA256-derived keystream/XOR construction with Encrypt-then-MAC. The implementation is not AES-GCM, despite AES-GCM being described by existing release/status documentation.

This is a **CRITICAL documentation/implementation mismatch** and a security-hardening priority. No encryption implementation was changed during Phase 0.

### Security check

The existing security-check path has previously been identified as reporting hard-coded checks rather than performing a complete real security scan. This is a **CRITICAL product-trust issue** and is scheduled for Phase 2.

### Secret ignore policy

The baseline `.gitignore` covers Python/build artifacts but does not comprehensively cover common secret/configuration files such as `.env`, key/certificate/token patterns, or credentials. This is a **HIGH priority** hardening item.

## Memory baseline

The current memory implementation is process-local/in-memory rather than persistent. This is treated as a product limitation for the later persistent-memory phase, not as a Phase 0 blocker.

## Test baseline

Repository documentation reports 79/79 tests passing. The GitHub connector used for this audit can inspect repository state but did not execute a local `pytest` process in this chat. Therefore the 79/79 claim is recorded as repository-reported, not independently re-executed during Phase 0.

## Documentation baseline

`PROJECT_STATUS.md` is dated 2026-07-26 and reports 100% completion, no known issues, and production readiness. The baseline audit has identified material issues that make those claims stale/incomplete for the current repository state. Documentation truthfulness will be corrected as part of the hardening phases.

## Baseline risk register

| ID | Finding | Severity | Planned phase |
|---|---|---|---|
| SEC-001 | Documented AES-GCM does not match the actual custom encryption construction | Critical | Phase 1 |
| SEC-002 | Security check does not provide a trustworthy real security scan | Critical | Phase 2 |
| SEC-003 | Secret-file ignore policy is incomplete | High | Phase 1 |
| CI-001 | CI does not run the full test suite | High | Phase 3/4 |
| CI-002 | CI mutates `pyproject.toml` as a packaging workaround | High | Phase 5 |
| MEM-001 | Long-term memory is process-local rather than persistent | High | Phase 7 |
| DOC-001 | Project status/release claims are stale relative to current implementation | Medium | Phase 1/13 |
| REL-001 | `main` has advanced beyond the `v1.0.0` tag | Medium | Release planning |

## Phase 0 completion criteria

- [x] Capture current `main` SHA.
- [x] Capture current tree identity.
- [x] Record release/tag relationship.
- [x] Record repository structure and major subsystems.
- [x] Record CI and packaging baseline.
- [x] Record critical/high security findings.
- [x] Record test-verification limitation.
- [x] Preserve this baseline in Git history before implementation changes.

## Next phase

**Phase 1 — Security Truth & Hardening.**

Phase 1 will address the critical/high security-trust issues first, with changes isolated in dedicated branches and validated through tests/CI before merge.
