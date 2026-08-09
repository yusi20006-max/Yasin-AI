# Yasin-AI Security Truth Baseline

## Purpose

This document records the security claims that must match the implementation. It is intentionally conservative: a feature is considered secure only when the repository contains an implementation and tests that demonstrate the claimed property.

## Phase 1 findings

### Encryption

The encryption module currently implements a custom stream/XOR construction authenticated with HMAC-SHA256. It must not be described as AES-GCM. Until the implementation is migrated to a standard AEAD construction, documentation must use neutral wording such as **authenticated encryption** and must not claim AES-GCM.

### Security checks

`yasin security check` currently reports a static set of successful checks rather than inspecting the repository/runtime. It must not be presented as a vulnerability scanner. A real scanner is planned for Phase 2.

### Secrets

Secret-bearing local files must be excluded from version control and must be covered by automated secret scanning before a production release.

### Authentication/session state

Password hashing and constant-time verification are present, but in-memory sessions are process-local. This is acceptable for the current single-process baseline but is not yet a distributed production session store.

### Memory

The current long-term memory implementation is process-local and non-persistent. It must not be described as durable storage until persistence is implemented.

## Phase 1 acceptance criteria

- No documentation claims AES-GCM unless the code actually uses AES-GCM.
- Security output does not claim vulnerability scanning that is not implemented.
- Secret-bearing local files are excluded by repository policy.
- Existing security tests remain compatible with the corrected claims.
- Critical security/documentation contradictions are removed without changing unrelated architecture.

## Scope boundary

This document does not certify the system as secure. It records known truth and establishes the boundary for subsequent hardening work. Phase 2 will implement real security checks and CI enforcement.
