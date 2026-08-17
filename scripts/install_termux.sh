#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# Yasin-AI Termux bootstrap.
# Termux currently ships Python 3.14; do not force an older Python.
# cryptography's prebuilt Android wheel can be ABI-incompatible with the
# Termux Python build, so build cryptography from source against this Python.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pkg update -y
pkg install -y \
  python clang rust make pkg-config openssl openssl-tool libffi git cmake patchelf

PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 14):
    raise SystemExit(f"Yasin-AI Termux bootstrap expects current Termux Python >=3.14; found {sys.version.split()[0]}")
print(f"Using Python {sys.version.split()[0]}")
PY

rm -rf .venv
"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

# Never consume the Termux-incompatible Android cryptography wheel.
PIP_NO_BINARY=cryptography python -m pip install --no-cache-dir cffi cryptography

python - <<'PY'
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
print("cryptography native backend: OK")
print("AESGCM backend: OK")
PY

python -m pip install -e ".[dev]"
python - <<'PY'
import yasinai
print(f"Yasin-AI {getattr(yasinai, '__version__', 'unknown')}: import OK")
PY

python -m pytest -q

echo
printf '%s\n' 'Yasin-AI Termux installation completed successfully.'
printf '%s\n' 'Activate: source .venv/bin/activate'
printf '%s\n' 'CLI: yasin --help'
printf '%s\n' 'Runtime: yasin serve'
