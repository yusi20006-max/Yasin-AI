"""#134 — Ecosystem consumers must not depend on private Yasin-AI modules."""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PRIVATE_PACKAGES = (
    "knowledge_platform",
    "developer_platform",
    "security_platform",
)

PUBLIC_ENTRYPOINTS = (
    "yasinai",
    "yasinai.contracts",
    "yasinai.services",
    "yasinai.providers",
    "yasinai.integration",
    "yasinai.core.runtime",
    "yasinai.core.config",
    "yasinai.cli.main",
    "api_service",
    "observability",
)

# Integration clients are the consumer-facing reference surface.
# Service facades may wrap private platforms; that is intentional.
ECOSYSTEM_FACING = [
    ROOT / "yasinai" / "integration",
    ROOT / "yasinai" / "contracts",
]


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    return imported


@pytest.mark.parametrize("entry", PUBLIC_ENTRYPOINTS)
def test_public_entrypoint_importable(entry: str):
    importlib.import_module(entry)


def test_integration_layer_forbids_private_imports():
    violations: list[str] = []
    for directory in ECOSYSTEM_FACING:
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.py"):
            if path.name.startswith("_") and path.name != "__init__.py":
                continue
            imported = _top_level_imports(path)
            for pkg in PRIVATE_PACKAGES:
                if pkg in imported:
                    violations.append(f"{path.relative_to(ROOT)} imports {pkg}")
    assert not violations, "Private package leakage:\n" + "\n".join(violations)


def test_forbidden_import_guard_is_explicit():
    for pkg in PRIVATE_PACKAGES:
        mod = importlib.import_module(pkg)
        assert mod is not None


def test_public_api_contract_lists_private_modules():
    doc = (ROOT / "docs" / "PUBLIC_API_CONTRACT.md").read_text(encoding="utf-8")
    for pkg in PRIVATE_PACKAGES:
        assert pkg in doc
