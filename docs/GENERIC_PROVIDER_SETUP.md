# Generic Provider Setup

Yasin-AI can connect to an OpenAI-compatible API without adding a provider-specific adapter.

## First-time setup

Set the Yasin-AI master key in the process environment. It protects the encrypted provider credentials and is never written by Yasin-AI:

```bash
export YASINAI_MASTER_KEY='choose-a-strong-secret'
```

Then configure a provider:

```bash
yasin provider setup
```

The CLI asks for:

- provider name
- Base URL
- model
- API key (hidden input)

The API key is encrypted with the existing Yasin-AI AES-256-GCM security engine. Provider metadata is stored under `~/.config/yasinai/providers.json` (or the path in `YASINAI_PROVIDER_CONFIG`) with restrictive file permissions.

Remote Base URLs must use HTTPS. `localhost`, `127.0.0.1`, and `::1` are allowed over HTTP for local development.

## Multiple providers

```bash
yasin provider setup
yasin provider list
yasin provider use <name>
yasin provider test <name>
yasin provider remove <name>
```

The configured providers are loaded into the normal Yasin-AI provider registry at runtime. Consumers continue to use the existing public `GenerationService` and generation contracts.

No provider-specific code is required for a compatible gateway. For example, a compatible Iranian gateway can be configured by entering its Base URL, API key, and model name.

## Security notes

- API keys are never printed by the CLI.
- API keys are not stored as plaintext in the provider configuration file.
- API keys are not included in provider listing output.
- Real credentials must never be committed to the repository or used in CI tests.
