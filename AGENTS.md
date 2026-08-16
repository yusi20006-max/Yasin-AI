# YasinAI Agent Instructions

## Project

Name:
YasinAI

Version:
1.1.4


## Role

You are a software engineering agent working on the Yasin-AI project.

Your responsibility:
- Maintain the architecture and ecosystem boundaries defined in **YASIN-DOCS ADR-001**.
- Remember that Yasin-AI is the Canonical AI Platform of the Yasin ecosystem. It provides shared AI capabilities, not independent standalone orchestrators.
- Maintain clear boundaries with:
  * **Yasin-Core** (generic runtime & SDK)
  * **Yasin-Agent** (owns Agent planning & workflows)
  * **YasinHub** (owns control and global observability)
  * **YasinCLI** (owns the unified command line interface)
- Improve code quality, verify issues, and prepare production documentation updates.


---

# First Steps

Before making any changes:

1. Read:

- MASTER_PLAN.md
- README.md
- docs/ARCHITECTURE.md


2. Analyze:

- Project structure
- Dependencies
- Tests
- Existing modules


3. Create a short report before large changes.


---

# Architecture Rules


YasinAI is modular.

Main modules:
yasinai/
core/
cli/
deployment/
developer_platform/
security_platform/
knowledge_platform/


Do not merge modules together without approval.


Do not remove existing systems unless explicitly requested.


---

# Coding Rules


Follow:

- Clean Python architecture
- PEP8 style
- Clear naming
- Type hints when useful
- Documentation for public functions


Avoid:

- Duplicate code
- Temporary hacks
- Unused files
- Breaking changes


---

# Testing Rules


Before submitting changes:


Run:
pytest


Verify:

- Imports work
- Core starts
- CLI works
- Security modules work
- Memory system works


Every new feature should include tests.


---

# Security Rules


Never commit:
.env
*.key
*.token
credentials
passwords
private configuration


Check for secrets before Git commits.


---

# Git Rules


Commit messages should be clear.


Examples:
Add memory retrieval module
Fix security token validation
Improve CLI commands


Avoid:
update changes fix stuff


---

# Change Management


For major changes:


1. Explain the problem.

2. Explain the solution.

3. List modified files.

4. Run tests.

5. Report results.


Do not perform large refactors without approval.


---

# Release Rules


Current target:

YasinAI v1.1.4 — see `PROJECT_STATUS.md` for the authoritative current-state summary before starting any release work.


Before release:


Required:

- Tests passing
- Documentation updated
- Version updated
- Changelog updated
- No secrets
- Clean repository


---

# Developer Platform Rules


Preserve:


- Agent SDK
- Plugin SDK
- App SDK
- CLI
- Extension API


---

# Security Platform Rules


Preserve:


- Identity
- Authentication
- Authorization
- Encryption
- Key Management
- Audit
- Threat Detection


---

# Knowledge Platform Rules


Preserve:


- Memory
- Knowledge Graph
- Semantic Search
- Context Engine
- Reasoning


---

# Communication Format


When reporting work, use:


## Summary

What changed?


## Files

Which files changed?


## Tests

What was tested?


## Result

Current status.


---

# Final Instruction


Understand the system before editing.

Prefer safe incremental improvements.

The architecture is more important than quick changes.
