"""#138 — architecture layer dependency enforcement."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
            # also capture second-level for yasinai.*
            parts = node.module.split(".")
            if len(parts) >= 2 and parts[0] == "yasinai":
                found.add(".".join(parts[:2]))
    return found


def test_contracts_do_not_import_services_or_platforms():
    forbidden = {
        "yasinai.services",
        "yasinai.providers",
        "yasinai.integration",
        "knowledge_platform",
        "developer_platform",
        "security_platform",
    }
    violations = []
    for path in (ROOT / "yasinai" / "contracts").rglob("*.py"):
        imported = _imports(path)
        for f in forbidden:
            if f in imported:
                violations.append(f"{path.name} imports {f}")
    assert not violations, violations


def test_providers_do_not_import_private_platforms():
    # Provider configuration legitimately uses the platform-owned encryption
    # boundary; knowledge/developer layers remain forbidden dependencies.
    forbidden = {"knowledge_platform", "developer_platform"}
    violations = []
    for path in (ROOT / "yasinai" / "providers").rglob("*.py"):
        imported = _imports(path)
        for f in forbidden:
            if f in imported:
                violations.append(f"{path.name} imports {f}")
    assert not violations, violations


def test_architecture_doc_exists():
    assert (ROOT / "docs" / "ARCHITECTURE_BOUNDARIES.md").is_file()
