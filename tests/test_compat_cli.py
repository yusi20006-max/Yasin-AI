"""#133 — YasinCLI compatibility against Public API Contract v1."""
from __future__ import annotations

import ast
from pathlib import Path

from yasinai.cli.main import create_parser
from yasinai.integration import YasinCLIClient

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ("knowledge_platform", "developer_platform", "security_platform")


def test_cli_parser_public_entry():
    parser = create_parser()
    assert parser.prog == "yasin"
    actions = [a for a in parser._subparsers._actions if hasattr(a, "choices") and a.choices]
    choices = actions[0].choices if actions else {}
    for cmd in ("status", "memory", "security"):
        assert cmd in choices


def test_cli_client_forbidden_imports():
    path = ROOT / "yasinai" / "integration" / "cli_client.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for pkg in PRIVATE:
        assert pkg not in imported


def test_cli_client_capabilities():
    c = YasinCLIClient()
    assert set(c.capabilities()) >= {"memory_search", "generation", "rag"}
