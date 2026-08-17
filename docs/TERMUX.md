# Yasin-AI on Termux

Yasin-AI treats Termux on Android as a first-class deployment target.

## Current Termux Python

Current Termux releases ship the current Python line (3.14.x in the tested environment). Yasin-AI must not require an older Python merely because a PyPI Android wheel is unavailable or ABI-incompatible.

## Cryptography

Termux provides a native `python-cryptography` package. The Yasin-AI Termux bootstrap installs and uses that package inside a `--system-site-packages` virtual environment. This is intentional: the PyPI Android `cryptography` wheel and a source build both produced native-loader/toolchain failures in the tested Termux environment.

The bootstrap verifies `cryptography` and `AESGCM` before installing Yasin-AI and prevents pip dependency resolution from replacing the Termux-native package.

## Installation

From the repository root:

```bash
bash scripts/install_termux.sh
```

The bootstrap installs the required Termux packages, creates `.venv` with access to Termux-native packages, verifies cryptography, installs Yasin-AI and its test tools, and runs the full test suite.

## Required Termux packages

- `python`
- `python-cryptography`
- `clang`
- `rust`
- `make`
- `pkg-config`
- `openssl`
- `openssl-tool`
- `libffi`
- `git`
- `cmake`
- `patchelf`

`cargo` is provided by the Termux `rust` package and should not be installed as a separate package.

## Known compatibility rule

Do not install or upgrade `cryptography` from PyPI in the Termux deployment environment. Use the Termux-native package selected by the bootstrap.
