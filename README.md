# YasinAI

> Modular AI Platform — runtime, agents, memory, security, developer tools, and deployment.

## What is YasinAI?

YasinAI is a modular artificial intelligence ecosystem built to support AI agents, developer extensions, knowledge management, long-term memory, secure execution, application development, and automation — all as independent, composable platforms sitting on top of a shared core runtime.

For the full architecture and vision, see [`MASTER_PLAN.md`](./MASTER_PLAN.md). For technical/module-level detail, see [`ARCHITECTURE.md`](./ARCHITECTURE.md). If you are an AI coding agent (Codex, Aider, Claude Code, etc.) working on this repo, read [`AGENTS.md`](./AGENTS.md) first.

## Status

Target release: **v1.0.0** — GitHub production release in progress.

## Core Platforms

| Platform | Purpose | Location |
|---|---|---|
| Core Runtime | Module loading, service management, runtime lifecycle | `yasinai/core/` |
| Developer Platform | Agent/Plugin/App SDKs, CLI tools, generator, debugger, profiler | `developer_platform/` |
| Security Platform | Identity, auth, authorization, encryption, monitoring | `security_platform/` |
| Knowledge Platform | Memory, knowledge graph, semantic search, reasoning | `knowledge_platform/` |
| CLI System | Command-line management interface | `yasinai/cli/` |
| Deployment System | Installer, Docker support, packaging, health checks | `yasinai/deployment/` |

## CLI Quick Reference

```
yasin status
yasin agent create
yasin memory search
yasin security check
yasin package build
```

## Development Rules (summary)

- Keep components independent and modular.
- Preserve backward compatibility; don't remove modules without approval.
- Clean, clearly named, documented Python code. Tests required for core features.
- Never commit API keys, passwords, tokens, private credentials, or backup files.

See `MASTER_PLAN.md` for the complete rule set, release process, and roadmap.

## Roadmap

Planned for v2.x: distributed AI network, advanced automation, robotics integration, self-improvement systems, and a broader global AI ecosystem.

## License

TBD.
