"""
YasinAI Security Platform.
Exposes public APIs for Identity, Authentication, Authorization, Encryption, Monitoring, and Security Scanning.
"""

from security_platform.auth import AuthManager, Session
from security_platform.authorization import Permission, Policy, PolicyEngine
from security_platform.encryption import EncryptionEngine, SecretStore
from security_platform.identity import IdentityManager, Role, User
from security_platform.monitoring import AuditLogger, SecurityEvent, ThreatDetector
from security_platform.scanner import SecurityFinding, SecurityScanner

__all__ = [
    "AuditLogger",
    "AuthManager",
    "EncryptionEngine",
    "IdentityManager",
    "Permission",
    "Policy",
    "PolicyEngine",
    "Role",
    "SecretStore",
    "SecurityEvent",
    "SecurityFinding",
    "SecurityScanner",
    "Session",
    "ThreatDetector",
    "User",
]

YASINAI_PRIVATE_MODULE = True
