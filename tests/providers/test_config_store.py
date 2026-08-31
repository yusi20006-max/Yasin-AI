import json

import pytest

from yasinai.providers.config_store import ProviderConfigError, ProviderStore, validate_base_url  # noqa: I001


FIXTURE_KEY = "test-" + "fixture-key"


def test_validate_base_url_requires_https_for_remote():
    assert validate_base_url("https://example.com/v1/") == "https://example.com/v1"
    assert validate_base_url("http://localhost:8000/v1/") == "http://localhost:8000/v1"
    with pytest.raises(ProviderConfigError):
        validate_base_url("http://example.com/v1")


def test_store_persists_metadata_but_not_plaintext_key(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MASTER_KEY", "test-master-key")
    path = tmp_path / "providers.json"
    store = ProviderStore(path)
    store.save(
        name="gateway",
        base_url="https://example.com/v1",
        model="model-x",
        api_key=FIXTURE_KEY,
        make_default=True,
    )

    raw = path.read_text(encoding="utf-8")
    assert FIXTURE_KEY not in raw
    payload = json.loads(raw)
    assert payload["default"] == "gateway"
    assert payload["providers"]["gateway"]["model"] == "model-x"
    assert store.get("gateway")["api_key"] == FIXTURE_KEY
    assert store.default()["name"] == "gateway"


def test_store_supports_multiple_providers_and_default_switch(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MASTER_KEY", "test-master-key")
    store = ProviderStore(tmp_path / "providers.json")
    for name in ("one", "two"):
        store.save(
            name=name,
            base_url="https://example.com/v1",
            model="model",
            api_key=f"{name}-" + "fixture-key",
            make_default=name == "one",
        )

    assert {item["name"] for item in store.list()} == {"one", "two"}
    store.use("two")
    assert store.default()["name"] == "two"
    assert store.remove("two") is True
    assert store.default()["name"] == "one"
