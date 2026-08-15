# ADR-0012: Plugin Trust Model & Sandbox

**Status:** Accepted — trust policy enforced; **sandbox not implemented**  
**Date:** 2026-08-16

## Context

Plugins execute **in-process**. Issue #143 asks for isolation/sandboxing of untrusted plugins.

## Current controls

- `PluginRegistry` / `PluginSDK` default **refuse** plugins with `trusted=False`
- Opt-in `allow_untrusted=True` is for non-production/isolated experiments only
- No OS-level isolation, seccomp, containers-per-plugin, or capability drop per plugin

## Decision

1. **Keep** the trusted-by-default registration policy.
2. **Do not claim** sandboxing exists.
3. **Defer** true sandbox (subprocess/WASM/container) until a concrete product requirement funds the design.

## Threat model (honest)

| Threat | Mitigation today |
|---|---|
| Accidental untrusted plugin load | Default reject |
| Malicious trusted plugin | **Not mitigated** (same process) |
| Supply-chain plugin package | Operator responsibility |

## Verification

`tests/test_plugin_trust_assessment.py`
