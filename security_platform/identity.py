"""
Identity Module for YasinAI Security Platform.
Manages Users, Roles, and user-role associations.
"""

from typing import Dict, List, Optional, Set


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

    def __init__(self, username: str, roles: Optional[List[str]] = None, active: bool = True) -> None:
        self.username: str = username
        self.roles: Set[str] = set(roles) if roles else set()
        self.active: bool = active

    def add_role(self, role_name: str) -> None:
        """Assign a role to the user."""
        self.roles.add(role_name)

    def remove_role(self, role_name: str) -> bool:
        """Remove a role from the user. Returns True if removed."""
        if role_name in self.roles:
            self.roles.remove(role_name)
            return True
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
        self._users: Dict[str, User] = {}
        self._roles: Dict[str, Role] = {}

    def create_role(self, name: str, description: str = "") -> Role:
        """Create and register a security role."""
        if name in self._roles:
            raise ValueError(f"Role '{name}' already exists.")
        role = Role(name, description)
        self._roles[name] = role
        return role

    def get_role(self, name: str) -> Optional[Role]:
        """Look up a registered role."""
        return self._roles.get(name)

    def delete_role(self, name: str) -> bool:
        """Delete a registered role."""
        if name in self._roles:
            del self._roles[name]
            # Clean up users holding this role
            for user in self._users.values():
                user.remove_role(name)
            return True
        return False

    def create_user(self, username: str, roles: Optional[List[str]] = None, active: bool = True) -> User:
        """Create and register a user identity."""
        if username in self._users:
            raise ValueError(f"User '{username}' already exists.")

        # Verify roles exist if provided
        if roles:
            for r in roles:
                if r not in self._roles:
                    raise ValueError(f"Role '{r}' is not registered.")

        user = User(username, roles, active)
        self._users[username] = user
        return user

    def get_user(self, username: str) -> Optional[User]:
        """Look up a user identity."""
        return self._users.get(username)

    def delete_user(self, username: str) -> bool:
        """Delete a user identity."""
        if username in self._users:
            del self._users[username]
            return True
        return False

    def assign_role_to_user(self, username: str, role_name: str) -> bool:
        """Assign role to user if both exist."""
        user = self.get_user(username)
        role = self.get_role(role_name)
        if user and role:
            user.add_role(role_name)
            return True
        return False

    def revoke_role_from_user(self, username: str, role_name: str) -> bool:
        """Revoke a role from a user."""
        user = self.get_user(username)
        if user:
            return user.remove_role(role_name)
        return False

    def list_users(self) -> List[User]:
        """List all registered users."""
        return list(self._users.values())

    def list_roles(self) -> List[Role]:
        """List all registered roles."""
        return list(self._roles.values())
