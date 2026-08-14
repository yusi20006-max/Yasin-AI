# YasinPress ↔ Yasin-AI Integration

**Phase:** 4.4  
**Date:** 2026-08-14

YasinPress owns publishing/editorial workflows. Use `YasinPressClient`
for drafts and grounded research.

```python
from yasinai.integration import YasinPressClient
press = YasinPressClient()
press.index_source("s1", "source text")
press.draft("Write a release note…", provider="local")
press.research("What shipped in v1.1?", provider="local")
```

| Need | API |
|---|---|
| Draft copy | `draft` |
| Grounded research | `research` |
| Index sources | `index_source` |
