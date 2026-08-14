"""Phase 5.1 — static verification of production deployment profile."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_as_non_root():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "USER 10001:10001" in text or "USER 10001" in text
    assert "useradd" in text
    assert "HEALTHCHECK" in text
    assert "yasin status" in text


def test_dockerfile_does_not_copy_env_secrets_explicitly():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    # Must not COPY a live .env into the image
    assert "COPY .env" not in text
    assert "COPY *.pem" not in text


def test_production_compose_hardening():
    path = ROOT / "deploy" / "compose.production.yml"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "no-new-privileges:true" in text
    assert "cap_drop:" in text
    assert "ALL" in text
    assert "read_only: true" in text
    assert "healthcheck:" in text
    assert "yasinai-data" in text
    assert "pids_limit:" in text
    assert "mem_limit:" in text


def test_dev_compose_points_to_production_profile():
    text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "compose.production.yml" in text or "production" in text.lower()
    assert "no-new-privileges:true" in text
    assert "cap_drop:" in text


def test_env_example_exists_and_gitignore_blocks_secrets():
    assert (ROOT / ".env.example").is_file()
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (".env", "*.key", "*.pem", "*.token"):
        assert pattern in gitignore


def test_production_release_doc_present():
    text = (ROOT / "PRODUCTION_RELEASE.md").read_text(encoding="utf-8")
    assert "v1.1.0" in text
    assert "healthcheck" in text.lower() or "Health" in text
