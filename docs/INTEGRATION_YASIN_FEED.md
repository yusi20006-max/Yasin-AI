# YasinFeed ↔ Yasin-AI Integration

**Phase:** 4.4  
**Date:** 2026-08-14

> **Integration policy:** `YasinFeedClient` below is a supported reference
> wrapper, not a requirement. YasinFeed's shipped Yasin-AI provider integrates
> directly through the canonical public `yasinai.contracts` and
> `yasinai.services` surfaces. Both approaches remain supported; consumers do
> not need to migrate solely because of this policy.

YasinFeed owns feed/timeline aggregation. Use `YasinFeedClient` for
semantic ranking and card summaries.

```python
from yasinai.integration import YasinFeedClient
feed = YasinFeedClient()
feed.index_item("i1", "…")
feed.rank("topic")
feed.summarize_card("long text…", provider="local")
```

| Need | API |
|---|---|
| Rank feed items | `rank` |
| Index item text | `index_item` |
| Card summary | `summarize_card` |
