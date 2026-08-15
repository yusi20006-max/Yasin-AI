"""
Authentication Module for YasinAI Security Platform.
Manages user credentials, hashing, tokens, and active sessions.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time

from security_platform.identity import IdentityManager

logger = logging.getLogger(__name__)


class Session:
    """
    Represents an active user session.
    """

    def __init__(self, token: str, username: str, duration: int = 3600) -> None:
        self.token: str = token
        self.username: str = username
        self.created_at: float = time.time()
        self.expires_at: float = self.created_at + duration

    def is_expired(self) -> bool:
        """Check if session is past expiration time."""
        return time.time() > self.expires_at


class AuthManager:
    """
    Handles secure user login, password hashing, token validation, and session lifecycle.
    """

    def __init__(self, identity_manager: IdentityManager) -> None:
        self.identity_manager: IdentityManager = identity_manager
        self._user_secrets: dict[str, bytes] = {}      # username -> salt
        self._password_hashes: dict[str, bytes] = {}   # username -> PBKDF2 hash
        self._sessions: dict[str, Session] = {}        # token -> Session

    def register_credentials(self, username: str, password: str) -> None:
        """
        Securely register a user's password using PBKDF2 with SHA-256 and a random salt.
        """
        user = self.identity_manager.get_user(username)
        if not user:
            logger.error(f"Failed to register credentials: User '{username}' does not exist.")
            raise ValueError(f"Cannot register credentials: User '{username}' does not exist.")

        salt = secrets.token_bytes(16)
        # Use PBKDF2 with HMAC-SHA256
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)

        self._user_secrets[username] = salt
        self._password_hashes[username] = pwd_hash
        logger.info(f"Successfully registered secure credentials for user '{username}'.")

    def login(self, username: str, password: str, session_duration: int = 3600) -> str | None:
        """
        Authenticate user and return a secure session token if successful.
        """
        logger.debug(f"Login attempt for user: '{username}'")
        # Enforce maximum session duration of 24 hours (86400 seconds)
        if session_duration > 86400:
            logger.error(f"Login failed: Session duration {session_duration} exceeds maximum limit of 24 hours.")
            raise ValueError("Session duration exceeds maximum limit of 24 hours.")

        user = self.identity_manager.get_user(username)
        user_active = user.active if user else False

        salt = self._user_secrets.get(username)
        stored_hash = self._password_hashes.get(username)

        if user and user_active and salt and stored_hash:
            # Verify password hash
            test_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
            if hmac.compare_digest(stored_hash, test_hash):
                # Create session
                token = secrets.token_urlsafe(32)
                session = Session(token, username, duration=session_duration)
                self._sessions[token] = session
                logger.info(f"Successful login for user '{username}'. Session token generated.")
                return token
            else:
                logger.warning(f"Login failed for user '{username}': incorrect password.")
                return None
        else:
            # Perform dummy PBKDF2 hash to prevent timing attacks
            dummy_salt = b"\x00" * 16
            hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), dummy_salt, 600000)
            logger.warning(f"Login failed for user '{username}': user not found, inactive, or not registered.")
            return None

    def logout(self, token: str) -> bool:
        """
        Invalidate a session by token. Returns True if successfully logged out.
        """
        if token in self._sessions:
            session = self._sessions[token]
            logger.info(f"Logging out user '{session.username}' and invalidating session token.")
            del self._sessions[token]
            return True
        logger.warning("Logout failed: Invalid or inactive session token.")
        return False

    def validate_token(self, token: str) -> bool:
        """
        Check if a session token is valid and not expired.
        """
        session = self._sessions.get(token)
        if not session:
            logger.debug("Token validation: Session not found.")
            return False

        if session.is_expired():
            logger.info(f"Token validation: Session has expired for user '{session.username}'.")
            self.logout(token)
            return False

        # Ensure user is still active
        user = self.identity_manager.get_user(session.username)
        if not user or not user.active:
            logger.info(f"Token validation: User '{session.username}' is deleted or no longer active.")
            self.logout(token)
            return False

        logger.debug(f"Token validation: Token is valid for user '{session.username}'.")
        return True

    def get_session(self, token: str) -> Session | None:
        """
        Retrieve session if valid.
        """
        if self.validate_token(token):
            return self._sessions.get(token)
        return None
