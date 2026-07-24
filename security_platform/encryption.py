"""
Encryption and Key Management Module for YasinAI Security Platform.
Provides secure SHA-256 hashing, symmetric encryption/decryption, and a secure secret storage engine.
"""

import base64
import hashlib
import hmac
import secrets
from typing import Dict, Optional


class EncryptionEngine:
    """
    Symmetric encryption engine using HMAC-SHA256 CTR keystream generation (no external dependencies).
    """

    @staticmethod
    def hash_data(data: str) -> str:
        """
        Compute SHA-256 hex digest of given data string.
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_key() -> str:
        """
        Generate a cryptographically secure random key.
        """
        return secrets.token_hex(32)

    @classmethod
    def encrypt(cls, plaintext: str, key: str) -> str:
        """
        Encrypt a string using HMAC-SHA256 in CTR mode.
        Returns a base64-encoded string.
        """
        plaintext_bytes = plaintext.encode("utf-8")
        key_bytes = hashlib.sha256(key.encode("utf-8")).digest()

        # Generate 16 bytes random IV
        iv = secrets.token_bytes(16)

        # Keystream generation (similar to CTR mode)
        keystream = bytearray()
        block_idx = 0
        while len(keystream) < len(plaintext_bytes):
            counter_bytes = block_idx.to_bytes(4, byteorder="big")
            block = hmac.digest(key_bytes, iv + counter_bytes, hashlib.sha256)
            keystream.extend(block)
            block_idx += 1

        # XOR to get ciphertext
        ciphertext = bytes(p ^ k for p, k in zip(plaintext_bytes, keystream))

        # Combine IV and ciphertext and base64-encode
        combined = iv + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    @classmethod
    def decrypt(cls, ciphertext_b64: str, key: str) -> str:
        """
        Decrypt a base64-encoded CTR encrypted string.
        """
        combined = base64.b64decode(ciphertext_b64.encode("utf-8"))
        if len(combined) < 16:
            raise ValueError("Invalid ciphertext: too short.")

        iv = combined[:16]
        ciphertext = combined[16:]
        key_bytes = hashlib.sha256(key.encode("utf-8")).digest()

        # Re-generate keystream
        keystream = bytearray()
        block_idx = 0
        while len(keystream) < len(ciphertext):
            counter_bytes = block_idx.to_bytes(4, byteorder="big")
            block = hmac.digest(key_bytes, iv + counter_bytes, hashlib.sha256)
            keystream.extend(block)
            block_idx += 1

        # XOR to restore plaintext
        plaintext_bytes = bytes(c ^ k for c, k in zip(ciphertext, keystream))
        return plaintext_bytes.decode("utf-8")


class SecretStore:
    """
    A secure storage dictionary for credentials, API tokens, and private configurations.
    """

    def __init__(self, encryption_engine: EncryptionEngine) -> None:
        self.engine: EncryptionEngine = encryption_engine
        self._secrets: Dict[str, str] = {}  # name -> encrypted secret (b64)

    def set_secret(self, name: str, secret_value: str, master_key: str) -> None:
        """
        Encrypts and stores a secret key-value.
        """
        encrypted = self.engine.encrypt(secret_value, master_key)
        self._secrets[name] = encrypted

    def get_secret(self, name: str, master_key: str) -> Optional[str]:
        """
        Decrypts and retrieves a stored secret.
        """
        encrypted = self._secrets.get(name)
        if not encrypted:
            return None
        try:
            return self.engine.decrypt(encrypted, master_key)
        except Exception:
            return None

    def delete_secret(self, name: str) -> bool:
        """
        Removes a stored secret.
        """
        if name in self._secrets:
            del self._secrets[name]
            return True
        return False

    def list_secrets(self) -> list:
        """
        List the names of stored secrets (values remain hidden/encrypted).
        """
        return list(self._secrets.keys())
