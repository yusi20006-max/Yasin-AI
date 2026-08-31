# Yasin-AI Capability Contract v1

This document defines the first stable, transport-neutral public boundary for ecosystem consumers.

## Contract identity

- Contract: `v1`
- Service: `yasinai`
- Current implementation: `1.1.4`
- Private provider, storage, and service implementation modules are not part of the contract.

## Capabilities

`GET /v1/capabilities` returns the version and currently exposed capability names.

The initial capability is `generation`.

## Generation

`POST /v1/generation`

Request fields:

- `prompt` — required non-empty string
- `model` — optional model identifier
- `provider` — optional provider identifier
- `system_prompt` — optional system instruction
- `max_tokens` — integer from 1 to 32000; default 1024
- `temperature` — number from 0.0 to 2.0; default 0.7
- `stop_sequences` — optional list of strings
- `metadata` — optional object for caller context

Response fields:

- `contract_version`
- `success`
- `text`
- `model`
- `provider`
- `input_tokens`
- `output_tokens`
- `finish_reason`
- `error`

## Error semantics

Malformed requests return status `400` with a safe `error` message. Unexpected handler failures return status `500` with `internal server error`; implementation details are not exposed.

Provider failures are represented by the existing `GenerationResult` contract and do not expose credentials or provider internals.

## Compatibility

Consumers must depend on the public contract and adapters only. They must not import `yasinai.providers`, private service internals, SQLite internals, or provider SDKs.

New fields may be added compatibly. Existing required field meanings and validation must not be changed within v1 without an explicit compatibility decision.

## Transport

The contract is transport-neutral. HTTP, CLI, and other transports may map to the same API service boundary without changing capability semantics.

## Security

Authentication and authorization are transport/deployment concerns and must be enforced by the concrete external adapter. The capability service itself must never treat caller-supplied metadata as authorization.

No credentials are required for deterministic contract tests.
