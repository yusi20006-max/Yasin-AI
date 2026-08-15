"""
Authorization Module for YasinAI Security Platform.
Manages permissions, policies, access rules, and role-based access control (RBAC).
"""
from __future__ import annotations

import logging

from security_platform.identity import IdentityManager

logger = logging.getLogger(__name__)


class Permission:
    """
    Represents an action or access point within the system.
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name: str = name
        self.description: str = description

    def __repr__(self) -> str:
        return f"Permission(name={self.name!r})"


class Policy:
    """
    Defines which roles are granted a set of permissions.
    """

    def __init__(self, name: str, allowed_roles: list[str], permissions: list[str]) -> None:
        self.name: str = name
        self.allowed_roles: set[str] = set(allowed_roles)
        self.permissions: set[str] = set(permissions)

    def permits(self, roles: set[str], permission: str) -> bool:
        """Check if policy permits any of the given roles to access a permission."""
        if permission not in self.permissions:
            return False
        # If there's an intersection between roles and allowed_roles, permit access
        return bool(roles & self.allowed_roles)

    def __repr__(self) -> str:
        return f"Policy(name={self.name!r}, roles={list(self.allowed_roles)}, permissions={list(self.permissions)})"


class PolicyEngine:
    """
    Evaluates permissions and implements Role-Based Access Control (RBAC).
    """

    def __init__(self, identity_manager: IdentityManager) -> None:
        self.identity_manager: IdentityManager = identity_manager
        self._permissions: dict[str, Permission] = {}
        self._policies: dict[str, Policy] = {}

    def create_permission(self, name: str, description: str = "") -> Permission:
        """Create and register a system permission."""
        if name in self._permissions:
            logger.error(f"Cannot create permission: '{name}' already exists.")
            raise ValueError(f"Permission '{name}' already exists.")
        permission = Permission(name, description)
        self._permissions[name] = permission
        logger.info(f"Successfully registered system permission: '{name}'")
        return permission

    def get_permission(self, name: str) -> Permission | None:
        """Look up a registered permission."""
        return self._permissions.get(name)

    def create_policy(self, name: str, allowed_roles: list[str], permissions: list[str]) -> Policy:
        """Create and register an authorization policy."""
        if name in self._policies:
            logger.error(f"Cannot create policy: '{name}' already exists.")
            raise ValueError(f"Policy '{name}' already exists.")

        # Verify permissions and roles exist/are known
        for perm in permissions:
            if perm not in self._permissions:
                logger.error(f"Cannot create policy '{name}': permission '{perm}' is not registered.")
                raise ValueError(f"Permission '{perm}' is not registered.")
        for role in allowed_roles:
            if not self.identity_manager.get_role(role):
                logger.error(f"Cannot create policy '{name}': role '{role}' is not registered in identity system.")
                raise ValueError(f"Role '{role}' is not registered in the Identity System.")

        policy = Policy(name, allowed_roles, permissions)
        self._policies[name] = policy
        logger.info(f"Successfully registered authorization policy: '{name}'")
        return policy

    def get_policy(self, name: str) -> Policy | None:
        """Look up a registered policy."""
        return self._policies.get(name)

    def is_authorized(self, username: str, permission_name: str) -> bool:
        """
        Evaluate if a user has access to a specific permission under existing policies.
        """
        logger.debug(f"Evaluating authorization for user '{username}' and permission '{permission_name}'")
        user = self.identity_manager.get_user(username)
        if not user or not user.active:
            logger.warning(f"Authorization denied: User '{username}' not found or inactive.")
            return False

        # If permission is not registered, deny access
        if permission_name not in self._permissions:
            logger.warning(f"Authorization denied: Permission '{permission_name}' is not registered.")
            return False

        # Evaluate against all active policies
        for policy in self._policies.values():
            if policy.permits(user.roles, permission_name):
                logger.debug(f"Authorization granted: policy '{policy.name}' permits access.")
                return True

        logger.info(f"Authorization denied: No policy permits user '{username}' for '{permission_name}'.")
        return False
