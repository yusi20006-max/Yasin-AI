# Gemini Provider

Phase 4 adds a Gemini provider to the existing Yasin-AI provider abstraction.

## Configuration

Set the API key outside the repository:

```bash
export GEMINI_API_KEY='...'
```

Optional model override:

```bash
export YASINAI_GEMINI_MODEL='gemini-3.6-flash'
```

Never commit the key or place it in source-controlled configuration.

## Routing

The default provider registry registers Gemini before LocalProvider. The existing `ProviderRouter` considers provider availability, so:

1. Configured Gemini is preferred.
2. If Gemini is not configured, LocalProvider can remain the available provider.
3. For an unpinned request, `GenerationService` keeps its existing bounded retry/fallback behavior.
4. An explicitly pinned provider is never silently replaced.
5. An explicit model constraint is preserved: fallback candidates must advertise the exact same model ID.

Local fallback reuses `LocalProvider` and its existing `LocalLLMRuntime`; the Gemini adapter never launches or manages the local process.

## API mapping

Gemini uses the REST `models.generateContent` endpoint. Yasin-AI maps the existing generation contract to `contents`, optional `systemInstruction`, and `generationConfig`, then maps text and usage metadata back into the provider-neutral `GenerationResponse`.

The public HTTP gateway remains provider-agnostic and continues to call `GenerationService`.

## Verification

Provider and routing tests use injectable transports/fakes and do not require a live Gemini key, external network, llama-server, or GGUF model.
