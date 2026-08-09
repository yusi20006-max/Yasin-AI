"""
Encryption and Key Management Module for YasinAI Security Platform.
Provides secure SHA-256 hashing, AEAD encryption/decryption, and secret storage.
"""

import base64
import hashlib
import logging
import os
import secrets
from typing import Dict, List, Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)


class EncryptionEngine:
    """Authenticated encryption engine using AES-256-GCM."""

    PBKDF2_ITERATIONS = 600_000
    SALT_SIZE = 16
    NONCE_SIZE = 12
    KEY_SIZE = 32

    @staticmethod
    def hash_data(data: str) -> str:
        """Compute a SHA-256 hex digest of the supplied string."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @classmethod
    def generate_key(cls) -> str:
        """Generate a cryptographically secure 256-bit key as hexadecimal text."""
        return secrets.token_hex(cls.KEY_SIZE)

    @classmethod
    def _derive_key(cls, key: str, salt: bytes) -> bytes:
        """Derive a 256-bit AES key from the caller-provided key and salt."""
        if not isinstance(key, str) or not key:
            raise ValueError("Encryption key must be a non-empty string.")
        return hashlib.pbkdf2_hmac(
            "sha256", key.encode("utf-8"), salt, cls.PBKDF2_ITERATIONS, dklen=cls.KEY_SIZE
        )

    @classmethod
    def encrypt(cls, plaintext: str, key: str) -> str:
        """Encrypt plaintext with AES-256-GCM and return base64 text.

        Serialized format: ``salt || nonce || ciphertext+tag``.
        """
        if not isinstance(plaintext, str):
            raise TypeError("Plaintext must be a string.")
        salt = secrets.token_bytes(cls.SALT_SIZE)
        nonce = secrets.token_bytes(cls.NONCE_SIZE)
        aes_key = cls._derive_key(key, salt)
        ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.b64encode(salt + nonce + ciphertext).decode("ascii")

    @classmethod
    def decrypt(cls, ciphertext_b64: str, key: str) -> str:
        """Decrypt and authenticate AES-256-GCM ciphertext."""
        try:
            combined = base64.b64decode(ciphertext_b64.encode("ascii"), validate=True)
        except (ValueError, UnicodeEncodeError) as exc:
            raise ValueError("Invalid ciphertext encoding.") from exc

        minimum_size = cls.SALT_SIZE + cls.NONCE_SIZE + 16
        if len(combined) < minimum_size:
            # Keep the established validation contract for existing callers.
            raise ValueError("Invalid ciphertext: too short for salt, MAC, and IV.")

        salt = combined[: cls.SALT_SIZE]
        nonce_start = cls.SALT_SIZE
        nonce_end = nonce_start + cls.NONCE_SIZE
        nonce = combined[nonce_start:nonce_end]
        ciphertext = combined[nonce_end:]
        aes_key = cls._derive_key(key, salt)

        try:
            plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext, None)
        except InvalidTag as exc:
            logger.warning("Decryption failed: AES-GCM authentication failed.")
            raise ValueError(
                "Ciphertext verification failed: authentication tag mismatch (HMAC mismatch)."
            ) from exc

        try:
            return plaintext.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Ciphertext decrypted to invalid UTF-8 data.") from exc


class SecretStore:
    """In-memory encrypted storage for credentials and private configuration."""

    def __init__(self, encryption_engine: EncryptionEngine) -> None:
        self.engine: EncryptionEngine = encryption_engine
        self._secrets: Dict[str, str] = {}

    def set_secret(self, name: str, secret_value: str, master_key: str) -> None:
        """Encrypt and store a secret after validating the environment master key."""
        expected_key = os.environ.get("YASINAI_MASTER_KEY")
        if not expected_key or master_key != expected_key:
            logger.error("SecretStore: master key validation failed.")
            raise ValueError(
                "Master key must be loaded strictly from an OS environment variable "
                "(specifically YASINAI_MASTER_KEY)."
            )
        self._secrets[name] = self.engine.encrypt(secret_value, master_key)

    def get_secret(self, name: str, master_key: str) -> Optional[str]:
        """Decrypt and retrieve a stored secret."""
        expected_key = os.environ.get("YASINAI_MASTER_KEY")
        if not expected_key or master_key != expected_key:
            logger.error("SecretStore: master key validation failed.")
            raise ValueError(
                "Master key must be loaded strictly from an OS environment variable "
                "(specifically YASINAI_MASTER_KEY)."
            )
        encrypted = self._secrets.get(name)
        if not encrypted:
            return None
        try:
            return self.engine.decrypt(encrypted, master_key)
        except ValueError as exc:
            logger.error("Error decrypting secret '%s': %s", name, exc)
            return None

    def delete_secret(self, name: str) -> bool:
        """Remove a secret from the in-memory store."""
        if name in self._secrets:
            del self._secrets[name]
            return True
        return False

    def list_secrets(self) -> List[str]:
        """List secret names without exposing secret values."""
        return list(self._secrets.keys())
