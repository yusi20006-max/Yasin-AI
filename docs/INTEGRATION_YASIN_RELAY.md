# YasinRelay ↔ Yasin-AI Integration

**Phase:** 4.4  
**Date:** 2026-08-14

> **Integration policy:** `YasinRelayClient` below is a supported reference
> wrapper, not a requirement. YasinRelay's shipped adapter integrates directly
> through the canonical public `yasinai.contracts` and `yasinai.services`
> surfaces. Both approaches remain supported; consumers do not need to migrate
> solely because of this policy.

YasinRelay owns message/event relay. Use `YasinRelayClient` for payload
enrichment and grounded answers — contracts/services only.

```python
from yasinai.integration import YasinRelayClient
relay = YasinRelayClient()
relay.enrich("event payload…", provider="local")
```

| Need | API |
|---|---|
| Transform/summarize payload | `enrich` |
| Context-grounded enrich | `grounded_enrich` |
