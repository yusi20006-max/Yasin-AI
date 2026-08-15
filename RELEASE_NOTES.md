# YasinAI Release Notes

## YasinAI v1.1.4

YasinAI v1.1.4 is the audited release candidate following the final security, CLI, CI/CD, and documentation hardening pass.

### Security and correctness

- Unified `security check` CLI execution around the canonical `SecurityScanner` implementation.
- Removed the simulated/hard-coded security-check result path from the primary CLI handler.
- Direct module and installed CLI security checks now use the same scanner and result semantics.
- Preserved provider credential handling and internal-error redaction guarantees.

### Quality gates

- Python compatibility matrix: 3.9, 3.10, 3.11, and 3.12.
- Ruff linting is blocking in CI.
- Dependency vulnerability scanning uses `pip-audit`.
- Repository security checks are executed by CI.
- Docker build and smoke-test validation are part of the release gates.

### Release verification

- Version: `1.1.4`
- Release tag: `v1.1.4`
- Release target: `main`
- Release should be published only after all required CI/security/Docker checks pass on the final release commit.

### Known design limitations

- Plugins are trusted-code extensions and are not sandboxed.
- Session state is process-local unless an external distributed session store is supplied.
- External secrets-management and network-policy controls remain deployment concerns.

### Verification

Run the complete project test suite with:

```bash
pytest
```

Run the canonical security check with:

```bash
yasin security check
python -m yasinai.cli security check
```

Both commands must report the same scanner-backed result semantics.
