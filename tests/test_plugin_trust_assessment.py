"""#143 — plugin trust policy present; sandbox not claimed."""
from __future__ import annotations

from pathlib import Path

import pytest

from developer_platform.plugin import Plugin, PluginSDK
from developer_platform.sdk import PluginTrustError

ROOT = Path(__file__).resolve().parents[1]


def test_adr_states_no_sandbox():
    text = (ROOT / "docs" / "ADR_0012_PLUGIN_TRUST.md").read_text(encoding="utf-8")
    assert "sandbox not implemented" in text.lower() or "Do not claim" in text


def test_untrusted_plugin_rejected_by_default():
    sdk = PluginSDK()
    plugin = Plugin(name="x", version="1.0.0", trusted=False)
    with pytest.raises(PluginTrustError):
        sdk.register_plugin(plugin)


def test_no_sandbox_module():
    assert not (ROOT / "yasinai" / "sandbox").exists()
    assert not (ROOT / "developer_platform" / "sandbox.py").exists()
