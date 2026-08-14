# Plugin Trust Boundary — Production Policy

**Phase:** 5.2  
**Status:** Enforced in `PluginRegistry` (trusted-only by default)  
**Date:** 2026-08-14

---

## Policy statement

Yasin-AI plugins execute **in-process** in the same address space as the host
runtime. There is **no sandbox**, no process isolation, and no remote plugin
marketplace in the current release line (`v1.1.x`).

Therefore:

1. **Only trusted code may be registered as a plugin in production.**
2. Untrusted, third-party, or remotely downloaded plugin code must **not** be
   loaded into a production process.
3. Isolated plugin containerization is planned for a future major line
   (see PROJECT_STATUS → v1.2.0), not claimed here.

---

## Runtime enforcement

`developer_platform.sdk.PluginRegistry` defaults to `allow_untrusted=False`.

Registering a `PluginSpec` with `trusted=False` raises `PluginTrustError`
unless the registry was constructed with `allow_untrusted=True` (explicit
non-production escape hatch).

```python
from developer_platform.sdk import PluginRegistry, PluginSpec, PluginTrustError

registry = PluginRegistry()  # production default
registry.register(PluginSpec("safe", handler=lambda: None, trusted=True))

# Raises PluginTrustError:
registry.register(PluginSpec("remote", handler=lambda: None, trusted=False))
```

---

## Operator requirements

| Environment | Requirement |
|---|---|
| Production | Trusted plugins only; do not set `allow_untrusted=True` |
| CI / unit tests | May use trusted fixtures; untrusted only with explicit flag |
| Future sandbox | Out of scope until isolated execution ships |

---

## Related

- `SECURITY.md` — security boundaries
- `SECURITY_AUDIT_2026-08-09.md` — residual risk record
- `developer_platform/sdk.py` — enforcement implementation
