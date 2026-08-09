# Security Policy

## Supported versions

Security fixes are applied to the `main` branch and to the latest published release.

## Reporting a vulnerability

Please do not disclose exploitable vulnerabilities in public issues. Use GitHub's private vulnerability reporting/security-advisory mechanism for this repository when available. Include reproduction steps, affected component, impact, and a suggested mitigation when possible.

## Security boundaries

Yasin-AI is not certified as secure. Plugins currently execute in-process and must be treated as trusted code. Do not load untrusted plugins into a production process.

Secrets must be supplied through runtime configuration or a secret manager and must never be committed to the repository.

## Release security requirements

Before a release candidate is cut, CI must pass tests, coverage, repository secret-file checks, dependency auditing, and container smoke tests. Final release approval also requires a manual review of authentication, persistence, plugin trust boundaries, and deployment configuration.
