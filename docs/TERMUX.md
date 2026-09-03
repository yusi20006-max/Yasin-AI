# Yasin-AI Termux Android ARM64 Compatibility Contract

Yasin-AI treats Termux on Android 11+ ARM64 (API level 30+) as a first-class deployment target.

## Target Runtime Contract

- **Platform:** Android 11+ (API level 30+)
- **Architecture:** ARM64 / aarch64
- **Environment:** Termux
- **Python Version:** Python 3.14.x (tested target: Python 3.14.6)
- **Bootstrap Command:** `bash scripts/install_termux.sh`

## Native Dependency & Cryptography Behavior

### Known ABI Issue
When installing `cryptography` via standard PyPI wheels on Android/Termux, the dynamic extension loader (Bionic) may fail with:
```
ImportError: dlopen failed: cannot locate symbol "PyModule_Type" referenced by .../cryptography/hazmat/bindings/_rust.abi3.so
```
This occurs because generic PyPI wheels target glibc or CPython ABI linkage where executable symbols are dynamically exported differently than in Android Bionic.

### Canonical Solution
Termux provides a native `python-cryptography` package built and linked specifically for Termux CPython and OpenSSL. The Yasin-AI bootstrap:
1. Installs Termux-native packages (`python-cryptography`, `clang`, `rust`, `openssl`, `libffi`, etc.) using `pkg install`.
2. Creates a Python virtual environment with `--system-site-packages` enabled.
3. Verifies `cryptography` and `AESGCM` natively before installing Yasin-AI.
4. Installs `yasinai` using `--no-deps` to prevent `pip` from replacing the native ABI-matched `python-cryptography` package.

### Security Requirement Compliance
This solution:
- Retains full cryptographic security and AESGCM encryption (`security_platform.encryption`).
- Preserves TLS and certificate validation capabilities.
- Avoids insecure fallbacks, plaintext stubs, or monkey-patching CPython symbols.

## Distinction: GitHub CI vs. Termux Verification

- **GitHub Actions CI:** Runs on x86_64 Ubuntu Linux runners. It verifies Python 3.14 syntax, code logic, unit tests, and cross-platform surface compatibility.
- **Actual Termux Runtime Verification:** Requires execution on physical or emulated Android 11+ ARM64 hardware. GitHub CI results verify build/code correctness but do **not** claim actual Termux hardware runtime execution. When actual Termux hardware is unavailable during execution, verification state is reported as `TERMUX_RUNTIME_VERIFICATION = NOT_EXECUTED`.

## Installation Procedure

From the repository root on Termux:

```bash
bash scripts/install_termux.sh
```

## Required Termux Packages

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

Note: `cargo` is provided directly by Termux `rust` and must not be installed separately.

## Operational Rules

Do not run `pip install --upgrade cryptography` inside the Termux virtual environment without preserving `--no-deps` or system site-packages, as doing so will replace the ABI-matched native package with an incompatible PyPI wheel.
