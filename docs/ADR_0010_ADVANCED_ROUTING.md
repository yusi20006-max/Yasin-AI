# ADR-0010: Advanced Provider Routing

**Status:** Accepted — **defer implementation**  
**Date:** 2026-08-16  
**Platform:** Yasin-AI 1.1.4

## Context

Issue #141 requests health-aware routing, cost-aware routing, load balancing, provider health registry, and advanced fallback.

Current implementation already provides:
- Explicit provider/model pinning
- Bounded per-provider retries
- Bounded multi-provider fallback (when not pinned)
- Explicit `allow_fallback` on `ProviderRouter.select`

## Decision

**Do not implement** cost-aware, health-aware, or load-balanced routing in 1.1.x.

Rationale:
1. No measured production traffic or cost telemetry pipeline exists yet.
2. Health registry without external probes would invent false signals.
3. False claims about intelligent routing would violate documentation honesty rules.

## Consequences

- Document advanced routing as **PLANNED / NOT CURRENTLY IMPLEMENTED**.
- Preserve existing bounded fallback behavior and model constraints.
- Revisit when ecosystem provides health/cost signals and explicit product requirements.

## Verification

`tests/test_advanced_routing_status.py` asserts documentation truth and that current router has no cost/health APIs.
