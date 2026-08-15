"""
Monitoring and Audit Logging Module for YasinAI Security Platform.
Records security events and contains rule-based heuristics for threat detection.
"""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class SecurityEvent:
    """
    Represents a specific auditable security event in the system.
    """

    def __init__(self, event_type: str, username: str, status: str, details: str, severity: str = "low") -> None:
        self.timestamp: float = time.time()
        self.event_type: str = event_type
        self.username: str = username
        self.status: str = status  # e.g., "success", "failure"
        self.details: str = details
        self.severity: str = severity  # "low", "medium", "high", "critical"

    def to_dict(self) -> dict[str, Any]:
        """Convert security event to dictionary format."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "username": self.username,
            "status": self.status,
            "details": self.details,
            "severity": self.severity
        }

    def __repr__(self) -> str:
        return f"SecurityEvent(type={self.event_type!r}, user={self.username!r}, status={self.status!r}, severity={self.severity!r})"


class AuditLogger:
    """
    Collects, filters, and records system security events.
    """

    def __init__(self) -> None:
        self._events: list[SecurityEvent] = []

    def log_event(self, event_type: str, username: str, status: str, details: str, severity: str = "low") -> SecurityEvent:
        """
        Record a security event to the audit trail.
        """
        event = SecurityEvent(event_type, username, status, details, severity)
        self._events.append(event)
        logger.info(f"AuditLog Event registered: {event}")
        return event

    def get_logs(self, event_type: str | None = None, username: str | None = None, min_severity: str | None = None) -> list[SecurityEvent]:
        """
        Filter and return matching logs.
        """
        logger.debug(f"Retrieving audit logs with filters: event_type={event_type}, username={username}, min_severity={min_severity}")
        severity_ranks: dict[str, int] = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        filtered: list[SecurityEvent] = self._events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if username:
            filtered = [e for e in filtered if e.username == username]
        if min_severity:
            min_rank = severity_ranks.get(min_severity.lower(), 1)
            filtered = [e for e in filtered if severity_ranks.get(e.severity.lower(), 1) >= min_rank]

        return filtered

    def clear(self) -> None:
        """Clear all records from audit logs."""
        logger.info("Clearing audit logs.")
        self._events.clear()


class ThreatDetector:
    """
    Analyzes audit logs using heuristic rules to flag potential security threats.
    """

    def __init__(self, audit_logger: AuditLogger) -> None:
        self.audit_logger: AuditLogger = audit_logger

    def detect_threats(self) -> list[dict[str, Any]]:
        """
        Scan logs to identify known patterns of malicious behavior.
        Currently supports:
          - Brute Force Login: 3+ consecutive/recent failed login attempts.
          - Multi-Access Denied: 3+ authorization/access failures.
          - Deactivated User Access Attempt: 1+ attempt of access by an inactive/deleted user profile.
        """
        logger.debug("Running threat detection scan on audit logs...")
        threats: list[dict[str, Any]] = []
        logs = self.audit_logger.get_logs()

        # Group login failure counts by user
        login_failures: dict[str, int] = {}
        # Group access denied counts by user
        access_denied_counts: dict[str, int] = {}

        for log in logs:
            user = log.username

            # 1. Brute Force Check
            if log.event_type == "login" and log.status == "failure":
                login_failures[user] = login_failures.get(user, 0) + 1
            elif log.event_type == "login" and log.status == "success":
                # Successful login resets failed counter
                login_failures[user] = 0

            # 2. Authorization Privilege Escalation Check
            if log.event_type == "authorization" and log.status == "failure":
                access_denied_counts[user] = access_denied_counts.get(user, 0) + 1

            # 3. Inactive/Disabled User Access Attempt Check
            if "inactive user" in log.details.lower() or "disabled user" in log.details.lower():
                threats.append({
                    "type": "InactiveUserAccessAttempt",
                    "username": user,
                    "description": f"Access attempt by inactive or disabled user: {user}",
                    "severity": "high",
                    "timestamp": log.timestamp
                })

        # Flag detected Brute Force
        for user, failures in login_failures.items():
            if failures >= 3:
                threats.append({
                    "type": "BruteForceAttack",
                    "username": user,
                    "description": f"User '{user}' has {failures} consecutive failed login attempts.",
                    "severity": "critical",
                    "timestamp": time.time()
                })

        # Flag detected Privilege Abuse / Multi-Access Denied
        for user, denials in access_denied_counts.items():
            if denials >= 3:
                threats.append({
                    "type": "PrivilegeAbuse",
                    "username": user,
                    "description": f"User '{user}' had {denials} unauthorized resource access requests.",
                    "severity": "medium",
                    "timestamp": time.time()
                })

        if threats:
            logger.warning(f"Threat detection scan completed: {len(threats)} potential threat(s) detected!")
        else:
            logger.debug("Threat detection scan completed. No threats identified.")
        return threats
