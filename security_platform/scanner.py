"""Repository and runtime security checks for YasinAI.

The scanner is deliberately deterministic and conservative. It reports only
checks that can be evaluated locally and does not claim external vulnerability
intelligence.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class SecurityFinding:
    id: str
    name: str
    passed: bool
    severity: str
    details: str
    path: Optional[str] = None


class SecurityScanner:
    """Run deterministic repository/runtime security checks."""

    SECRET_PATTERNS = (
        ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
        ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
        ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("generic_secret", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*[\"'][^\"']{12,}[\"']")),
    )
    SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
    TEXT_SUFFIXES = {".py", ".toml", ".yml", ".yaml", ".json", ".ini", ".cfg", ".conf", ".txt", ".md", ".sh", ".env"}
    SECRET_FILENAMES = {".env", ".env.local", ".env.production", "credentials", "credentials.json"}

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def _iter_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(self.root)
            if any(part in self.SKIP_DIRS for part in relative.parts):
                continue
            if path.suffix.lower() in self.TEXT_SUFFIXES or path.name in self.SECRET_FILENAMES:
                yield path

    def check_secrets(self) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        for path in self._iter_files():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern_name, pattern in self.SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(SecurityFinding("SEC_SECRET_001", "Potential secret exposure", False, "critical", f"Potential {pattern_name} detected in scanned source material.", str(path.relative_to(self.root))))
                    break
        if not findings:
            findings.append(SecurityFinding("SEC_SECRET_001", "Repository secret scan", True, "critical", "No supported high-confidence secret patterns were detected in scanned text files."))
        return findings

    def check_secret_policy(self) -> SecurityFinding:
        ignore = self.root / ".gitignore"
        if not ignore.exists():
            return SecurityFinding("SEC_POLICY_001", "Secret ignore policy", False, "high", ".gitignore is missing.")
        text = ignore.read_text(encoding="utf-8", errors="ignore")
        required = {".env", "*.key", "*.pem", "*.token"}
        missing = sorted(item for item in required if item not in text)
        if missing:
            return SecurityFinding("SEC_POLICY_001", "Secret ignore policy", False, "high", f"Missing ignore patterns: {', '.join(missing)}")
        return SecurityFinding("SEC_POLICY_001", "Secret ignore policy", True, "high", "Repository ignores common secret-bearing files.")

    def check_file_permissions(self) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        for path in self._iter_files():
            try:
                mode = path.stat().st_mode
            except OSError:
                continue
            if mode & 0o002:
                findings.append(SecurityFinding("SEC_PERM_001", "World-writable source file", False, "high", "A scanned source/configuration file is world-writable.", str(path.relative_to(self.root))))
        if not findings:
            findings.append(SecurityFinding("SEC_PERM_001", "File permissions", True, "high", "No scanned source/configuration files are world-writable."))
        return findings

    def check_crypto(self) -> SecurityFinding:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from security_platform.encryption import EncryptionEngine
            if AESGCM is None or not hasattr(EncryptionEngine, "encrypt"):
                raise RuntimeError("required AEAD implementation is unavailable")
            return SecurityFinding("SEC_CRYPTO_001", "Authenticated encryption", True, "critical", "AES-GCM dependency and encryption engine are available.")
        except Exception as exc:
            return SecurityFinding("SEC_CRYPTO_001", "Authenticated encryption", False, "critical", f"Encryption security check failed: {exc}")

    def check_policy_files(self) -> SecurityFinding:
        required = ["SECURITY_TRUTH.md", "AGENTS.md"]
        missing = [name for name in required if not (self.root / name).exists()]
        if missing:
            return SecurityFinding("SEC_POLICY_002", "Security policy documentation", False, "medium", f"Missing policy files: {', '.join(missing)}")
        return SecurityFinding("SEC_POLICY_002", "Security policy documentation", True, "medium", "Security truth and engineering policy documents are present.")

    def scan(self) -> Dict[str, object]:
        findings: List[SecurityFinding] = []
        findings.extend(self.check_secrets())
        findings.append(self.check_secret_policy())
        findings.extend(self.check_file_permissions())
        findings.append(self.check_crypto())
        findings.append(self.check_policy_files())
        failed = [f for f in findings if not f.passed]
        return {
            "status": "SECURE" if not failed else "VULNERABLE",
            "scanned_items": len(findings),
            "failed_items": len(failed),
            "scanner": "repository-runtime-security-v1",
            "scope": ["secret-pattern scan", "secret ignore policy", "file permissions", "crypto availability", "security policy files"],
            "findings": [asdict(f) for f in findings],
        }
