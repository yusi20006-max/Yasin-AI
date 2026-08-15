# API Error Contract

**Platform:** Yasin-AI 1.1.4  
**Transport:** `api_service.APIService` (framework-neutral)

## Response shape

Successful and error responses share a JSON-compatible `data` mapping.

| Case | HTTP status | `data` |
|---|---|---|
| Success | 200 | handler result mapping |
| Route not found | 404 | `{"error": "route not found"}` |
| Validation / client error (`ValidationError` / `APIError`) | `exc.status_code` (default 400) | `{"error": "<safe message>"}` |
| Unhandled exception | 500 | `{"error": "internal server error"}` |

## Rules

1. **Never leak internals** — stack traces, provider raw bodies, database strings, or secret material must not appear in `data`.
2. **Log full detail internally** for 500s (`logger.exception`).
3. **Stable keys** — error bodies always expose exactly `{"error": "..."}`.
4. **Auth failures** (when auth middleware is present) should use 401/403 with the same shape.
5. **Provider failures** surfaced through handlers should be mapped to 502/503 with a **generic** message (not raw provider text).

## Verification

`tests/test_api_error_contract.py`
