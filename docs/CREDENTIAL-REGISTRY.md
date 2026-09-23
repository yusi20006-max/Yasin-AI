# Yasin-AI Credential Registry

The credential registry is the source of truth for credentials imported from API Token Manager.

## Import flow

1. API Token Manager validates a credential.
2. The user explicitly selects **Import to Yasin-AI**.
3. Yasin-AI authenticates the bridge request using `YASINAI_BRIDGE_TOKEN` and exact `YASINAI_ALLOWED_ORIGIN`.
4. Yasin-AI validates the credential server-side. Client health results are never trusted.
5. Only a validation result with `authenticated=true` and no validation `error_code` is persisted.
6. Downstream applications use Yasin-AI as the credential source instead of storing provider API keys themselves.

## API

### POST /v1/token/import

Request:

```json
{"provider":"openai","credential":"<secret>","model":"gpt-4o-mini","label":"primary","metadata":{"source":"token-manager"}}
```

The response contains only the stable credential ID and non-secret metadata plus validation health. The credential is never echoed.

### GET /v1/token/credentials

Returns non-secret registry records. The credential field is never exposed.

## Storage

The default path is `$XDG_CONFIG_HOME/yasinai/credentials.json`, or `~/.config/yasinai/credentials.json` when XDG is unset. The file is owner-readable/writable (`0600`) and the parent directory is `0700`. The registry replaces files atomically.
