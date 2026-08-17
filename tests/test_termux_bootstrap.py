from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_termux.sh"
DOC = ROOT / "docs" / "TERMUX.md"


def test_termux_bootstrap_exists_and_is_fail_fast() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text
    assert "python-cryptography" in text
    assert "--system-site-packages" in text
    assert "pip install -e \".[dev]\" --no-deps" in text
    assert "cryptography.exceptions import InvalidTag" in text
    assert "cryptography.hazmat.primitives.ciphers.aead import AESGCM" in text
    assert "PIP_NO_BINARY=cryptography" not in text


def test_termux_docs_match_bootstrap() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "Python 3.14" in text
    assert "python-cryptography" in text
    assert "system-site-packages" in text
    assert "scripts/install_termux.sh" in text
