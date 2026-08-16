# YasinAI MASTER PLAN

## Project Identity

Name:
YasinAI (Canonical AI Platform)

Version Target:
v1.1.4

Type:
Canonical AI Capability Platform of the Yasin Ecosystem (YASIN-DOCS ADR-001)

Goal:
Provide shared AI capabilities (embeddings, provider routing, inference, semantic retrieval, RAG, and durable memory contracts) for the Yasin ecosystem while preserving strict boundaries with Yasin-Core, Yasin-Agent, YasinHub, YasinCLI, YasinRelay, YasinFeed, and YasinPress.

---

# Vision

YasinAI is designed as a modular artificial intelligence platform.

The system should support:

- AI Agents
- Developer Extensions
- Knowledge Management
- Long Term Memory
- Secure Execution
- Application Development
- Automation

---

# Core Architecture

```
                      YasinAI
                         |
                   Core Runtime
                         |
      ┌──────────────────┼──────────────────┐
  Developer          Security            Knowledge
  Platform           Platform            Platform
      |                  |                    |
      └──────────────────┼────────────────────┘
                         |
                 Application Layer
                         |
                Users / Developers
```

---

# Main Components

## 1. Core Runtime

Purpose:

The central execution engine of YasinAI.

Responsibilities:

- Module loading
- Service management
- Runtime lifecycle
- System configuration

Location:
yasinai/core/

---

## 2. Developer Platform

Purpose:

Provide tools for developers to create AI extensions.

Features:

- Agent SDK
- Plugin SDK
- Application SDK
- CLI Tools
- Generator
- Debugger
- Profiler
- Extension API
- Package Builder

Location:
developer_platform/

---

## 3. Security Platform

Purpose:

Protect users, data and AI components.

Features:

### Identity

- User Identity
- Roles

### Authentication

- Login System
- Token Management
- Sessions

### Authorization

- Permission Engine
- Policy Engine
- Access Control

### Encryption

- Data Protection
- Hashing
- Key Management
- Secret Storage

### Monitoring

- Audit Logs
- Security Events
- Threat Detection

Location:
security_platform/

---

## 4. Knowledge Platform

Purpose:

Give YasinAI memory and knowledge capabilities.

Features:

### Memory

- Short Term Memory
- Long Term Memory

### Knowledge Graph

- Entities
- Relations
- Triple Store
- Query Engine

### Search

- Vector Store
- Embedding Engine
- Semantic Search
- Retriever

### Context

- Conversation Memory
- Context Builder

### Reasoning

- Knowledge Reasoner
- Rule Engine

Location:
knowledge_platform/

---

## 5. CLI System

Purpose:

Command line management interface.

Commands & Usage:

```bash
# General platform/runtime diagnostics (supports --json)
yasin status [--json]

# Create a custom AI Agent (supports --role, --description, --type, and --json)
yasin agent create [name] --role [role] --description [description] --type [type] [--json]

# Query the semantic memory store (supports --limit, --threshold, and --json)
yasin memory search [query] --limit [limit] --threshold [threshold] [--json]

# Run platform security checks and vulnerability scans (supports --json)
yasin security check [--json]

# Build deployment artifacts and packages (supports --output, --version, and --json)
yasin package build --output [directory] --version [version] [--json]
```

Location:
yasinai/cli/

---

## 6. Deployment System

Purpose:

Make YasinAI installable and portable.

Features:

- Installer
- Docker Support
- Package Builder
- Environment Check
- Health Check

Location:
yasinai/deployment/

---

# Development Phases & Release State

We classify milestones to distinguish clearly between current stable baselines and active development lines:

### CURRENT BASELINE
- **v1.1.4 (Audit/Correctness/Security Hardening)**: Provider abstraction with concrete adapters, bounded retry/fallback, generation and RAG service boundaries, local persistent memory/knowledge with concurrency hardening, security controls, observability, packaging, CI (Ruff, pip-audit, security gate, Docker smoke) and production container baseline.
- **v1.1.0 – v1.1.3**: Historical maintenance releases — see `PROJECT_STATUS.md` release table and `CHANGELOG.md` for details.
- **v1.0.0 (Production Release)**: Baseline production launch featuring memory pipelines, developer platforms, and core runtimes.

### ACTIVE DEVELOPMENT
- **Ecosystem Contract Verification**: Verify capability-contract conformance across Yasin-Agent, YasinHub, YasinCLI, YasinRelay, YasinFeed and YasinPress, and confirm no consumer imports private Yasin-AI implementation modules.

### PLANNED FUTURE VERSIONS
- **v1.2.0 (Minor Release)**: Cost-aware and health-aware provider routing, automatic multi-node provider failover, model registry, inference guardrails, and isolated plugin sandboxing.
- **v2.0.0 (Major Release)**: Distributed/HA persistence, agent collaboration networks, and YasinHub telemetry endpoints.

---

# Development Rules

## Architecture Rules

- Do not remove modules without approval.
- Keep components independent.
- Preserve backward compatibility.
- Prefer modular design.

## Code Rules

- Clean Python structure.
- Clear naming.
- Documentation required.
- Tests required for core features.

## Security Rules

Never commit:

- API keys
- Passwords
- Tokens
- Private credentials
- Backup files

---

# Current Mission

Verify ecosystem-wide capability contracts and architecture boundaries before controlled integration migration.

Tasks:
1. Ecosystem contract verification and boundary tests across Yasin-Agent, YasinHub, YasinCLI, YasinRelay, YasinFeed and YasinPress (Active).
2. Capability-contract conformance tests confirming no consumer imports private provider, storage, CLI or implementation modules (Active).
3. Re-baseline the roadmap for advanced provider routing, plugin sandboxing and distributed/HA persistence (Planned — see `PROJECT_STATUS.md`).

See `PROJECT_STATUS.md` for the authoritative current-state summary and `VERSIONING_POLICY.md` for version governance.

---

# Agent Instructions

Any AI coding agent working on this project must:

1. Read this file first.
2. Read VERSIONING_POLICY.md.
3. Understand architecture before editing.
4. Create a report before major changes.
5. Avoid destructive modifications.
6. Keep changes documented.

---

End of MASTER PLAN
