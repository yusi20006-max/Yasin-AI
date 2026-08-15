# YasinAI Release Checklist

Version: `v1.1.4`

Status: Release Candidate — pending final CI verification

---

## Repository and source

- [x] Repository and default branch verified
- [x] Version metadata synchronized to `1.1.4`
- [x] Source syntax/import audit completed
- [x] No known duplicate security implementation remains on the supported CLI paths

## Runtime and platform

- [x] Runtime starts successfully
- [x] Bootstrap and configuration paths verified
- [x] Agent SDK verified
- [x] Plugin trust boundary documented
- [x] Memory and knowledge services verified
- [x] Package Builder verified

## Security

- [x] Authentication and authorization reviewed
- [x] Encryption and key handling reviewed
- [x] Provider credentials are environment-only
- [x] Sensitive provider errors are redacted
- [x] Repository security scanner is real and CI-backed
- [x] `yasin security check` uses the canonical `SecurityScanner`
- [x] `python -m yasinai.cli security check` uses the canonical scanner path
- [x] No known committed secrets

## CLI

- [x] `yasin status`
- [x] `yasin agent create`
- [x] `yasin memory search`
- [x] `yasin security check`
- [x] `yasin package build`

## Tests and CI

- [x] Unit/integration test suite defined
- [x] Python 3.9–3.12 matrix configured
- [x] Ruff lint gate configured
- [x] `pip-audit` dependency gate configured
- [x] Security gate configured
- [x] Docker build/smoke gate configured
- [ ] Final CI run on the post-audit commit is green

## Documentation

- [x] README and architecture documentation reviewed
- [x] Security documentation reviewed
- [x] Version references aligned to `1.1.4` where applicable
- [x] Release notes updated for `v1.1.4`

## Deployment

- [x] Dockerfile reviewed
- [x] Production compose hardening reviewed
- [x] Non-root container execution configured
- [x] Production read-only/capability restrictions reviewed
- [x] Docker smoke test configured

## Release integrity

- [x] Release tag `v1.1.4` points to the intended release line
- [x] Release target is `main`
- [ ] Publish GitHub Release only after final CI/security/Docker verification

## Final approval

Do not publish the release while any required CI, security, or Docker gate is failing.

### Release commands

```bash
git tag -a v1.1.4 -m "v1.1.4 Release"
git push origin v1.1.4
```

The tag must remain immutable after publication.
