# Yasin-AI on Termux

Yasin-AI treats Termux on Android as a first-class deployment target.

## Current Termux Python

Current Termux releases may ship Python 3.14. Yasin-AI must not require an older Python merely because an Android wheel is unavailable or incompatible.

The Termux bootstrap builds `cryptography` from source so its native extension is compiled against the exact Python/Android environment in use. This avoids the `PyLong_Type` dynamic-loader failure observed with the prebuilt Android wheel.

## Installation

From the repository root:

```bash
bash scripts/install_termux.sh
```

The bootstrap installs the required Termux toolchain, creates `.venv`, installs `cryptography` from source, verifies its native backend, installs Yasin-AI, and runs the test suite.

## Required Termux packages

- `python`
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

Do not force a prebuilt `cryptography` wheel on Termux. The bootstrap uses `PIP_NO_BINARY=cryptography` intentionally.
