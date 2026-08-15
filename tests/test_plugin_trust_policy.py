"""Phase 5.2 — plugin trust boundary production policy tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from developer_platform.sdk import (
    PluginRegistry,
    PluginSpec,
    PluginTrustError,
    plugin,
)

ROOT = Path(__file__).resolve().parents[1]


def test_policy_document_exists():
    path = ROOT / "docs" / "PLUGIN_TRUST_POLICY.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "trusted" in text.lower()
    assert "sandbox" in text.lower() or "in-process" in text.lower()


def test_security_md_references_trust_policy():
    text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "PLUGIN_TRUST_POLICY" in text or "trusted code" in text


def test_registry_accepts_trusted_plugin():
    reg = PluginRegistry()
    spec = PluginSpec(name="ok", handler=lambda: "ok", trusted=True)
    assert reg.register(spec) is spec
    assert reg.invoke("ok") == "ok"


def test_registry_rejects_untrusted_by_default():
    reg = PluginRegistry()
    with pytest.raises(PluginTrustError, match="untrusted"):
        reg.register(PluginSpec(name="bad", handler=lambda: None, trusted=False))


def test_registry_allows_untrusted_when_explicitly_enabled():
    reg = PluginRegistry(allow_untrusted=True)
    reg.register(PluginSpec(name="lab", handler=lambda: 1, trusted=False))
    assert reg.invoke("lab") == 1


def test_decorator_defaults_to_trusted():
    @plugin("decorated")
    def handler():
        return 42

    spec = handler.__yasinai_plugin__
    assert spec.trusted is True
    reg = PluginRegistry()
    reg.register(spec)
    assert reg.invoke("decorated") == 42


def test_decorator_untrusted_flag():
    @plugin("remoteish", trusted=False)
    def handler():
        return 0

    assert handler.__yasinai_plugin__.trusted is False
