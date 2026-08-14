"""Phase 5.3 — production readiness gate checks for v1.1.x maintenance line."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_version_sources_aligned():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.1.0"' in pyproject
    init = (ROOT / "yasinai" / "__init__.py").read_text(encoding="utf-8")
    # version may be defined as string constant
    assert "1.1.0" in init or "1.1" in init


def test_phase3_capability_modules_present():
    assert (ROOT / "yasinai" / "providers" / "openai_provider.py").is_file()
    assert (ROOT / "yasinai" / "providers" / "anthropic_provider.py").is_file()
    assert (ROOT / "yasinai" / "providers" / "local_provider.py").is_file()
    assert (ROOT / "yasinai" / "services" / "generation_service.py").is_file()
    assert (ROOT / "yasinai" / "services" / "rag_service.py").is_file()
    assert (ROOT / "yasinai" / "contracts" / "generation.py").is_file()
    assert (ROOT / "yasinai" / "contracts" / "rag.py").is_file()


def test_phase4_integration_clients_present():
    integ = ROOT / "yasinai" / "integration"
    for name in (
        "agent_client.py",
        "hub_client.py",
        "cli_client.py",
        "relay_client.py",
        "feed_client.py",
        "press_client.py",
    ):
        assert (integ / name).is_file(), name


def test_phase5_hardening_artifacts_present():
    assert (ROOT / "docs" / "PLUGIN_TRUST_POLICY.md").is_file()
    assert (ROOT / "tests" / "test_production_profile.py").is_file()
    assert (ROOT / "deploy" / "compose.production.yml").is_file()
    assert (ROOT / ".env.example").is_file()


def test_ci_coverage_gate_configured():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "cov-fail-under" in ci
    assert "pip_audit" in ci or "pip-audit" in ci
    assert "security check" in ci


def test_release_checklist_mentions_phase_gates():
    text = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    assert "v1.1.0" in text
    # Phase 5.3 expands checklist — must mention providers or generation or RAG
    assert any(
        token in text
        for token in ("Provider", "Generation", "RAG", "Integration", "Phase 5")
    )


def test_public_imports_smoke():
    from yasinai.contracts import GenerationRequest, RagRequest
    from yasinai.services import GenerationService, KnowledgeService, RagService
    from yasinai.integration import (
        YasinAgentClient,
        YasinCLIClient,
        YasinFeedClient,
        YasinHubClient,
        YasinPressClient,
        YasinRelayClient,
    )
    from yasinai.providers import LocalProvider, build_default_registry

    assert GenerationRequest and RagRequest
    assert GenerationService and KnowledgeService and RagService
    assert all(
        [
            YasinAgentClient,
            YasinHubClient,
            YasinCLIClient,
            YasinRelayClient,
            YasinFeedClient,
            YasinPressClient,
        ]
    )
    reg = build_default_registry()
    assert reg.get("local") is not None or any(
        p.info.name == "local" for p in reg.available_for_capability(
            __import__("yasinai.providers", fromlist=["ProviderCapability"]).ProviderCapability.GENERATION
        )
    ) or LocalProvider().is_available()
