# Managed Local LLM Runtime

Yasin-AI can manage a local `llama-server` process through `LocalLLMRuntime`.

## Boundary

The runtime manager owns the external process lifecycle only:

```text
LocalLLMRuntime
    |
    +-- start / stop / restart
    +-- PID and process identity
    +-- port conflict detection
    +-- readiness /health probe
    +-- persistent runtime state
          |
          v
      llama-server
```

Inference/provider behavior remains a separate concern. This Issue does not
replace the existing `LocalProvider` implementation or add the public HTTP AI
Gateway.

## Configuration

Create a `LocalLLMRuntimeConfig` with an explicit executable, GGUF model path,
port, and optional runtime arguments. User-specific absolute paths must stay
outside repository configuration.

The default state file is `~/.config/yasinai/local-llm-runtime.json` and is
written with restrictive permissions where the platform permits it.

## Safety behavior

- An already-owned healthy process is reused by `start`.
- A stale PID/state record is cleared after process identity verification.
- A port occupied by another process is reported as a conflict.
- `stop` verifies the stored PID, process start time, executable identity, and
  configured port before signalling a persisted process.
- Startup timeout terminates the process and removes runtime state.
- Missing executable/model and process startup failures are surfaced as
  `LocalLLMRuntimeError` without exposing command output or secrets.

## Verification

The runtime considers a server ready only after a successful local HTTP probe
against `/health` or `/v1/models`.

Focused tests are in `tests/runtime/test_local_llm.py`. They use a temporary
fake HTTP server and never require a real GGUF model or a user's local paths.
