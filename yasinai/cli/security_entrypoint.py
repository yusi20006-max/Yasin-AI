"""Security-aware console entrypoint for YasinAI."""

from __future__ import annotations

import importlib
import json
import sys


def _finding_id(finding: dict) -> str | None:
    """Return a finding identifier when present, without requiring it."""
    value = finding.get("id")
    if value is None:
        return None
    return str(value)


def security_check(argv: list[str]) -> int:
    """Run the canonical scanner with a stable CLI presentation.

    All security decisions and values come from ``SecurityScanner``. The
    ``checks`` compatibility field and legacy heading are presentation-only;
    they never contain hard-coded pass/fail results. Scanner findings may be
    represented by older/partial schemas, so presentation must not crash when
    optional metadata such as ``id`` or ``path`` is absent.
    """
    from security_platform.scanner import SecurityScanner

    json_output = "--json" in argv
    report = SecurityScanner().scan()

    findings = report.get("findings", [])
    report["checks"] = findings[:4]

    if json_output:
        print(json.dumps(report, indent=2))
    else:
        print("=========================================")
        print("YasinAI Security Platform - Audit Check")
        print(f"Status: {report.get('status', 'UNKNOWN')}")
        print("=========================================")
        for finding in findings:
            passed = bool(finding.get("passed", False))
            status = "[ PASS ]" if passed else "[ FAIL ]"
            name = finding.get("name", "Unnamed security check")
            severity = finding.get("severity", "unknown")
            location = f" ({finding['path']})" if finding.get("path") else ""
            details = finding.get("details", "")
            print(f"{status} {name} [{severity}]{location}")
            print(f"         Details: {details}")

        # Backward-compatible human-readable alias for the canonical secret
        # scan. It is printed only from the actual scanner result. Older report
        # schemas may omit the optional finding id, so lookup must be tolerant.
        secret_finding = next(
            (item for item in findings if _finding_id(item) == "SEC_SECRET_001"),
            None,
        )
        if secret_finding is not None:
            status = "[ PASS ]" if bool(secret_finding.get("passed", False)) else "[ FAIL ]"
            print(f"{status} Environment Secrets Check (canonical repository secret scan)")
        print("=========================================")
        print(f"Scan complete. {report.get('scanned_items', len(findings))} checks performed.")

    return 0 if report.get("failed_items", 0) == 0 else 1


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) >= 2 and args[0] == "security" and args[1] == "check":
        raise SystemExit(security_check(args[2:]))

    cli = importlib.import_module("yasinai.cli.main")
    cli.main(args)
