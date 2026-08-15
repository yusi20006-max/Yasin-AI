# Performance Baseline

**Platform:** Yasin-AI 1.1.4  
**Environment:** CI runners / local developer machines (not production SLAs)

## Measured operations (deterministic, no network)

| Operation | Baseline target | Notes |
|---|---|---|
| Local provider generate (stub) | < 50 ms / call | In-process stub |
| Memory store + list (short-term, 20 entries) | < 200 ms | SQLite-backed |
| Knowledge semantic query (small corpus) | < 500 ms | TF-IDF/local retriever |
| ProviderRouter.select | < 5 ms | In-memory registry |

These are **engineering baselines**, not contractual SLOs. No throughput/latency claims for cloud providers.

## Verification

`tests/test_performance_baseline.py`
