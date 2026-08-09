# Deployment baseline

This directory contains the supported local/container deployment baseline for Yasin-AI.

The Compose definition is intentionally conservative: persistent data is isolated in a named volume, the container filesystem is read-only, Linux capabilities are dropped, and privilege escalation is disabled.
