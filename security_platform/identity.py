"""
Identity Module for YasinAI Security Platform.
Manages Users, Roles, and user-role associations.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class Role:
    """
    Represents a Security Role with associated descriptive metadata.
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name: str = name
        self.description: str = description

    def __repr__(self) -> str:
        return f"Role(name={self.name!r})"


class User:
    """
    Represents a User Identity within the YasinAI ecosystem.
    """

    def __init__(self, username: str, roles: list[str] | None = None, active: bool = True) -> None:
        self.username: str = username
        self.roles: set[str] = set(roles) if roles else set()
        self.active: bool = active

    def add_role(self, role_name: str) -> None:
        """Assign a role to the user."""
        logger.debug(f"Assigning role '{role_name}' to user '{self.username}'")
        self.roles.add(role_name)

    def remove_role(self, role_name: str) -> bool:
        """Remove a role from the user. Returns True if removed."""
        if role_name in self.roles:
            self.roles.remove(role_name)
            logger.debug(f"Removed role '{role_name}' from user '{self.username}'")
            return True
        logger.warning(f"Role '{role_name}' not found for user '{self.username}' to remove.")
        return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has the specified role."""
        return role_name in self.roles

    def __repr__(self) -> str:
        return f"User(username={self.username!r}, roles={list(self.roles)}, active={self.active})"


class IdentityManager:
    """
    Manages user identities, roles, and administrative tasks.
    """

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._roles: dict[str, Role] = {}

    def create_role(self, name: str, description: str = "") -> Role:
        """Create and register a security role."""
        if name in self._roles:
            logger.error(f"Cannot create role: '{name}' already exists.")
            raise ValueError(f"Role '{name}' already exists.")
        role = Role(name, description)
        self._roles[name] = role
        logger.info(f"Successfully created role: '{name}'")
        return role

    def get_role(self, name: str) -> Role | None:
        """Look up a registered role."""
        return self._roles.get(name)

    def delete_role(self, name: str) -> bool:
        """Delete a registered role."""
        if name in self._roles:
            del self._roles[name]
            # Clean up users holding this role
            for user in self._users.values():
                user.remove_role(name)
            logger.info(f"Successfully deleted role '{name}' and updated associated users.")
            return True
        logger.warning(f"Attempted to delete non-existent role: '{name}'")
        return False

    def create_user(self, username: str, roles: list[str] | None = None, active: bool = True) -> User:
        """Create and register a user identity."""
        if username in self._users:
            logger.error(f"Cannot create user: '{username}' already exists.")
            raise ValueError(f"User '{username}' already exists.")

        # Verify roles exist if provided
        if roles:
            for r in roles:
                if r not in self._roles:
                    logger.error(f"Cannot create user '{username}': role '{r}' is not registered.")
                    raise ValueError(f"Role '{r}' is not registered.")

        user = User(username, roles, active)
        self._users[username] = user
        logger.info(f"Successfully created user identity: '{username}'")
        return user

    def get_user(self, username: str) -> User | None:
        """Look up a user identity."""
        return self._users.get(username)

    def delete_user(self, username: str) -> bool:
        """Delete a user identity."""
        if username in self._users:
            del self._users[username]
            logger.info(f"Successfully deleted user identity: '{username}'")
            return True
        logger.warning(f"Attempted to delete non-existent user: '{username}'")
        return False

    def assign_role_to_user(self, username: str, role_name: str) -> bool:
        """Assign role to user if both exist."""
        user = self.get_user(username)
        role = self.get_role(role_name)
        if user and role:
            user.add_role(role_name)
            logger.info(f"Successfully assigned role '{role_name}' to user '{username}'")
            return True
        logger.warning(f"Failed to assign role '{role_name}' to user '{username}' (existence check failed).")
        return False

    def revoke_role_from_user(self, username: str, role_name: str) -> bool:
        """Revoke a role from a user."""
        user = self.get_user(username)
        if user:
            revoked = user.remove_role(role_name)
            if revoked:
                logger.info(f"Successfully revoked role '{role_name}' from user '{username}'")
            return revoked
        logger.warning(f"Failed to revoke role '{role_name}' from user '{username}' (user not found).")
        return False

    def list_users(self) -> list[User]:
        """List all registered users."""
        return list(self._users.values())

    def list_roles(self) -> list[Role]:
        """List all registered roles."""
        return list(self._roles.values())
