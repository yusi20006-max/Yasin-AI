"""#140 — production readiness and resilience smoke."""
from __future__ import annotations

from pathlib import Path

from yasinai.core.runtime import Runtime

ROOT = Path(__file__).resolve().parents[1]


def test_production_readiness_doc_exists():
    text = (ROOT / "docs" / "PRODUCTION_READINESS.md").read_text(encoding="utf-8")
    assert "No HA" in text
    assert "Runtime.is_ready" in text


def test_production_compose_hardening_present():
    compose = (ROOT / "deploy" / "compose.production.yml").read_text(encoding="utf-8")
    assert "no-new-privileges" in compose
    assert "cap_drop" in compose


def test_runtime_survives_start_shutdown_cycle():
    rt = Runtime(config_defaults={"modules": []})
    rt.start()
    assert rt.is_ready()
    rt.shutdown()
    assert not rt.is_ready()


def test_dockerfile_non_root():
    df = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "USER 10001" in df or "USER 10001:10001" in df
