"""Security-aware console entrypoint for YasinAI."""

from __future__ import annotations

import importlib
import json
import sys


def security_check(argv: list[str]) -> int:
    """Run the canonical scanner with a stable CLI presentation.

    All security decisions and values come from ``SecurityScanner``.  The
    ``checks`` compatibility field and legacy heading are presentation-only;
    they never contain hard-coded pass/fail results.
    """
    from security_platform.scanner import SecurityScanner

    json_output = "--json" in argv
    report = SecurityScanner().scan()

    # Keep the JSON contract used by existing consumers while making the
    # canonical scanner report the sole source of truth.  The compatibility
    # list is derived directly from real findings and intentionally contains
    # no synthetic security result.
    report["checks"] = report["findings"][:4]

    if json_output:
        print(json.dumps(report, indent=2))
    else:
        print("=========================================")
        print("YasinAI Security Platform - Audit Check")
        print(f"Status: {report['status']}")
        print("=========================================")
        for finding in report["findings"]:
            status = "[ PASS ]" if finding["passed"] else "[ FAIL ]"
            location = f" ({finding['path']})" if finding.get("path") else ""
            print(f"{status} {finding['name']} [{finding['severity']}]{location}")
            print(f"         Details: {finding['details']}")
        # Backward-compatible human-readable alias for the canonical secret
        # scan. It is printed only from the actual scanner result.
        secret_finding = next(
            (item for item in report["findings"] if item["id"] == "SEC_SECRET_001"),
            None,
        )
        if secret_finding is not None:
            status = "[ PASS ]" if secret_finding["passed"] else "[ FAIL ]"
            print(f"{status} Environment Secrets Check (canonical repository secret scan)")
        print("=========================================")
        print(f"Scan complete. {report['scanned_items']} checks performed.")
    return 0 if report["failed_items"] == 0 else 1


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) >= 2 and args[0] == "security" and args[1] == "check":
        raise SystemExit(security_check(args[2:]))

    cli = importlib.import_module("yasinai.cli.main")
    cli.main(args)
