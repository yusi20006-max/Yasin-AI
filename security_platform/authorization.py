"""
Authorization Module for YasinAI Security Platform.
Manages permissions, policies, access rules, and role-based access control (RBAC).
"""

from typing import Dict, List, Optional, Set
from security_platform.identity import IdentityManager, User


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

    def __init__(self, name: str, allowed_roles: List[str], permissions: List[str]) -> None:
        self.name: str = name
        self.allowed_roles: Set[str] = set(allowed_roles)
        self.permissions: Set[str] = set(permissions)

    def permits(self, roles: Set[str], permission: str) -> bool:
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
        self._permissions: Dict[str, Permission] = {}
        self._policies: Dict[str, Policy] = {}

    def create_permission(self, name: str, description: str = "") -> Permission:
        """Create and register a system permission."""
        if name in self._permissions:
            raise ValueError(f"Permission '{name}' already exists.")
        permission = Permission(name, description)
        self._permissions[name] = permission
        return permission

    def get_permission(self, name: str) -> Optional[Permission]:
        """Look up a registered permission."""
        return self._permissions.get(name)

    def create_policy(self, name: str, allowed_roles: List[str], permissions: List[str]) -> Policy:
        """Create and register an authorization policy."""
        if name in self._policies:
            raise ValueError(f"Policy '{name}' already exists.")

        # Verify permissions and roles exist/are known
        for perm in permissions:
            if perm not in self._permissions:
                raise ValueError(f"Permission '{perm}' is not registered.")
        for role in allowed_roles:
            if not self.identity_manager.get_role(role):
                raise ValueError(f"Role '{role}' is not registered in the Identity System.")

        policy = Policy(name, allowed_roles, permissions)
        self._policies[name] = policy
        return policy

    def get_policy(self, name: str) -> Optional[Policy]:
        """Look up a registered policy."""
        return self._policies.get(name)

    def is_authorized(self, username: str, permission_name: str) -> bool:
        """
        Evaluate if a user has access to a specific permission under existing policies.
        """
        user = self.identity_manager.get_user(username)
        if not user or not user.active:
            return False

        # If permission is not registered, deny access
        if permission_name not in self._permissions:
            return False

        # Evaluate against all active policies
        for policy in self._policies.values():
            if policy.permits(user.roles, permission_name):
                return True

        return False
