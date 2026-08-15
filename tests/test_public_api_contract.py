"""#130 — automated verification of the frozen Public API Contract."""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

# Machine-readable public symbol registry (must match docs/PUBLIC_API_CONTRACT.md)
PUBLIC_IMPORTS: dict[str, list[str]] = {
    "yasinai": ["__version__"],
    "yasinai.contracts": [
        "CONTRACT_VERSION",
        "CapabilityError",
        "CapabilityMetadata",
        "CapabilityUnavailableError",
        "ContractViolationError",
        "ObservabilityContext",
        "MemoryType",
        "MemoryRequest",
        "MemoryResponse",
        "MemoryEntry",
        "KnowledgeQueryType",
        "KnowledgeQuery",
        "KnowledgeEntry",
        "KnowledgeResult",
        "GenerationRequest",
        "GenerationResult",
        "RagRequest",
        "RagResult",
        "EmbeddingRequest",
        "EmbeddingResponse",
        "EmbeddingVector",
        "PluginContract",
        "PluginInvokeRequest",
        "PluginInvokeResponse",
    ],
    "yasinai.services": [
        "KnowledgeService",
        "GenerationService",
        "RagService",
    ],
    "yasinai.providers": [
        "ProviderBase",
        "ProviderCapability",
        "ProviderInfo",
        "ProviderError",
        "ProviderRegistry",
        "ProviderRouter",
        "ProviderUnavailableError",
        "GenerationRequest",
        "GenerationResponse",
        "OpenAIProvider",
        "AnthropicProvider",
        "LocalProvider",
        "build_default_registry",
    ],
    "yasinai.integration": [
        "YasinAgentClient",
        "YasinHubClient",
        "YasinCLIClient",
        "YasinRelayClient",
        "YasinFeedClient",
        "YasinPressClient",
    ],
    "yasinai.core.runtime": ["Runtime"],
    "yasinai.core.config": ["Config"],
    "observability": ["Counter", "Timer", "MetricsRegistry"],
    "api_service": [],  # package importable
}

PRIVATE_PACKAGES = (
    "knowledge_platform",
    "developer_platform",
    "security_platform",
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("module_name,symbols", list(PUBLIC_IMPORTS.items()))
def test_public_module_importable(module_name: str, symbols: list[str]):
    mod = importlib.import_module(module_name)
    for name in symbols:
        assert hasattr(mod, name), f"{module_name}.{name} missing from public surface"


def test_contract_version_is_v1():
    from yasinai.contracts import CONTRACT_VERSION

    assert CONTRACT_VERSION == "v1"


def test_platform_version_present():
    import yasinai

    assert isinstance(yasinai.__version__, str) and yasinai.__version__


def test_public_api_contract_doc_exists():
    path = ROOT / "docs" / "PUBLIC_API_CONTRACT.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Public API Contract" in text
    assert "knowledge_platform" in text  # marked private
    assert "CONTRACT_VERSION" in text or "v1" in text


def test_integration_clients_do_not_import_private_packages():
    integ = ROOT / "yasinai" / "integration"
    for path in integ.glob("*.py"):
        if path.name.startswith("_"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        for forbidden in PRIVATE_PACKAGES:
            assert forbidden not in imported, f"{path.name} imports {forbidden}"
