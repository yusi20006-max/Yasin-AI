# ADR-0011: Distributed Persistence / HA

**Status:** Accepted — **do not implement in 1.1.x**  
**Date:** 2026-08-16

## Context

Issue #142 asks for distributed sessions/storage, multi-node coordination, and failover.

Current state:
- SQLite-backed memory/vector stores with configurable paths
- Single-process Runtime lifecycle
- No cluster membership or consensus layer

## Decision

**Defer HA / distributed persistence.** No speculative multi-node implementation.

Justification:
1. No ecosystem requirement document demands multi-node Yasin-AI today.
2. SQLite file stores are intentionally single-writer.
3. Implementing partial HA without proven failure tests would create false confidence.

## Accepted limitation

Yasin-AI 1.1.x is a **single-node** platform process. Horizontal scale is achieved by running multiple independent instances with external load balancing **outside** this repository's responsibility.

## Revisit triggers

- Explicit multi-writer storage requirement from YasinHub / Agent fleets
- Chosen distributed store (Postgres/Redis) with migration plan

## Verification

`tests/test_ha_assessment_status.py`
