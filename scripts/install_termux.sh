#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# Yasin-AI Termux Android ARM64 Bootstrap.
# Target runtime: Android 11+ ARM64 API level 30+ Termux Python 3.14.x
# Uses Termux-native python-cryptography to avoid PyO3/ABI dynamic loader failures.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pkg update -y
pkg install -y python python-cryptography clang rust make pkg-config openssl openssl-tool libffi git cmake patchelf

PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 14):
    print(f"Warning: Yasin-AI Termux bootstrap target is Python >=3.14; found {sys.version.split()[0]}")
print(f"Using Python {sys.version.split()[0]}")
PY

rm -rf .venv
"$PYTHON_BIN" -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

python - <<'PY'
import importlib.metadata as metadata
import sys
try:
    import cryptography
    import cffi
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception as exc:
    print(f"Termux cryptography/cffi check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
    raise SystemExit(20)
print(f"Termux cryptography {metadata.version('cryptography')}: import OK")
print(f"Termux cffi {metadata.version('cffi')}: import OK")
print("AESGCM backend: OK")
PY

# Install Yasin without dependency resolution so pip cannot overwrite the
# ABI-matched Termux cryptography package.
python -m pip install -e ".[dev]" --no-deps
python -m pip install 'pytest>=7.4,<10' 'pytest-cov>=6,<8'

python - <<'PY'
import yasinai
from yasinai import GenerationRequest, GenerationService
from yasinai.core.system import SystemInfo

info = SystemInfo().get_info()
print(f"Yasin-AI {getattr(yasinai, '__version__', 'unknown')}: import OK")
print(f"Canonical Public API import (GenerationRequest, GenerationService): OK")
print(f"System Info: {info}")
PY

python -m pytest -q

echo
printf '%s\n' 'Yasin-AI Termux installation completed successfully.'
printf '%s\n' 'Activate: source .venv/bin/activate'
printf '%s\n' 'CLI: yasin --help'
printf '%s\n' 'Runtime: yasin serve'
