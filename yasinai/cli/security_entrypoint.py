"""Security-aware console entrypoint for YasinAI."""

from __future__ import annotations

import importlib
import json
import sys


def security_check(argv: list[str]) -> int:
    from security_platform.scanner import SecurityScanner

    json_output = "--json" in argv
    report = SecurityScanner().scan()
    if json_output:
        print(json.dumps(report, indent=2))
    else:
        print("=========================================")
        print("YasinAI Security Platform - Real Audit")
        print(f"Status: {report['status']}")
        print("=========================================")
        for finding in report["findings"]:
            status = "[ PASS ]" if finding["passed"] else "[ FAIL ]"
            location = f" ({finding['path']})" if finding.get("path") else ""
            print(f"{status} {finding['name']} [{finding['severity']}]{location}")
            print(f"         Details: {finding['details']}")
        print("=========================================")
        print(f"Scan complete. {report['scanned_items']} checks performed.")
    return 0 if report["failed_items"] == 0 else 1


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) >= 2 and args[0] == "security" and args[1] == "check":
        raise SystemExit(security_check(args[2:]))

    cli = importlib.import_module("yasinai.cli.main")
    cli.main(args)
