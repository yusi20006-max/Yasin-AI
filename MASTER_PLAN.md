# YasinAI MASTER PLAN

## Project Identity

Name:
YasinAI (Canonical AI Platform)

Version Target:
v1.1.0

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
- **v1.1.0 (Maintenance Release)**: Consolidates codebase versioning and adds automated dependency security auditing to CI.
- **v1.0.0 (Production Release)**: Baseline production launch featuring memory pipelines, developer platforms, and core runtimes.

### ACTIVE DEVELOPMENT
- **Phase 2.3 (Version & Release Consistency)**: Align version sources of truth, establish standard versioning policies, and compatibility mappings.

### PLANNED FUTURE VERSIONS
- **v1.2.0 (Minor Release)**: Provider Gateway routing, model registry, inference guardrails, and isolated plugin sandboxing.
- **v2.0.0 (Major Release)**: Distributed AI Network, agent collaboration networks, and YasinHub telemetry endpoints.

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

Establish strict versioning and release source of truth.

Tasks:
1. Reconcile version references across all docs to point to `1.1.0` (Active).
2. Authorize standard versioning policy document (`VERSIONING_POLICY.md`) (Active).
3. Ensure no version drift across package metadata and runtime (Active).

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
