# ruff: noqa: I001
from pathlib import Path
from yasinai.core.system import SystemInfo, detect_android_api_level, detect_native_deps, detect_termux


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_termux.sh"
DOC = ROOT / "docs" / "TERMUX.md"


def test_termux_bootstrap_exists_and_is_fail_fast() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text
    assert "pkg install -y python python-cryptography" in text
    assert "--system-site-packages .venv" in text
    assert 'PYTHON_BIN="${PYTHON_BIN:-python}"' in text
    assert '"$PYTHON_BIN" -m venv --system-site-packages .venv' in text
    assert "--no-deps" in text
    assert "cryptography.exceptions import InvalidTag" in text
    assert "cryptography.hazmat.primitives.ciphers.aead import AESGCM" in text
    assert "PIP_NO_BINARY=cryptography" not in text


def test_termux_docs_match_bootstrap() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "Termux Android ARM64 Compatibility Contract" in text
    assert "python-cryptography" in text
    assert "--system-site-packages" in text
    assert "scripts/install_termux.sh" in text
    assert "TERMUX_RUNTIME_VERIFICATION = NOT_EXECUTED" in text


def test_native_crypto_and_cffi_dependencies_importable() -> None:
    import cffi
    import cryptography
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    assert cryptography.__version__
    assert cffi.__version__
    assert AESGCM and InvalidTag


def test_canonical_public_api_top_level_imports() -> None:
    import yasinai
    from yasinai import GenerationRequest, GenerationService

    assert yasinai.__version__
    req = GenerationRequest(prompt="test prompt")
    assert req.prompt == "test prompt"

    svc = GenerationService()
    assert svc is not None


def test_system_diagnostics_structure() -> None:
    info = SystemInfo().get_info()
    assert "python_version" in info
    assert "architecture" in info
    assert "platform" in info
    assert "is_termux" in info
    assert "android_api_level" in info
    assert "cryptography_version" in info
    assert "cffi_version" in info
    assert "openssl_version" in info

    assert isinstance(info["is_termux"], bool)
    assert info["cryptography_version"] is not None
    assert detect_termux() in (True, False)
    assert detect_android_api_level() is None or isinstance(detect_android_api_level(), int)
    assert isinstance(detect_native_deps(), dict)
