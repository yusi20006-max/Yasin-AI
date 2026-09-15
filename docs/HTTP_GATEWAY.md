# Yasin-AI HTTP Gateway

The public HTTP gateway is a transport adapter over the existing `GenerationService` boundary. It does not contain provider routing or process lifecycle logic.

## Start locally

```bash
yasin-ai-gateway
```

Defaults are deliberately local-only:

- Host: `127.0.0.1`
- Port: `8000`
- Override with `YASINAI_GATEWAY_HOST` and `YASINAI_GATEWAY_PORT`.

## Endpoints

### Health

`GET /health`

### Models

`GET /v1/models`

Returns available generation model IDs without provider secrets or private configuration.

### Chat completions

`POST /v1/chat/completions`

Example:

```json
{
  "model": "local-qwen17",
  "messages": [
    {"role": "system", "content": "Be concise."},
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 128,
  "temperature": 0.2
}
```

The gateway converts this request into the public `GenerationRequest` contract and delegates to `GenerationService`. Provider retry/fallback and model selection remain in that service layer.

## Security

The default bind address is loopback. Do not expose the gateway on a LAN/public interface without an explicit authentication and network-security decision. Request bodies are bounded to 1 MiB and error responses avoid returning internal exceptions.
