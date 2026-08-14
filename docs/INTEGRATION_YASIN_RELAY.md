# YasinRelay ↔ Yasin-AI Integration

**Phase:** 4.4  
**Date:** 2026-08-14

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
