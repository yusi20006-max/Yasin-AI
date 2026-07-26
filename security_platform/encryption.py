"""
Encryption and Key Management Module for YasinAI Security Platform.
Provides secure SHA-256 hashing, symmetric encryption/decryption, and a secure secret storage engine.
"""

import base64
import hashlib
import hmac
import os
import secrets
from typing import Dict, Optional


class EncryptionEngine:
    """
    Symmetric encryption engine using HMAC-SHA256 CTR keystream generation with
    Encrypt-then-MAC authentication for robust ciphertext integrity (no external dependencies).
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
        Encrypt a string using HMAC-SHA256 in CTR mode, with Encrypt-then-MAC authentication.
        Returns a base64-encoded string.
        """
        plaintext_bytes = plaintext.encode("utf-8")

        # Strengthen key derivation using PBKDF2 with HMAC-SHA256 and a random 16-byte salt
        salt = secrets.token_bytes(16)
        key_bytes = hashlib.pbkdf2_hmac("sha256", key.encode("utf-8"), salt, 100000)

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

        # Derive a distinct MAC key from key_bytes to keep encryption and MAC keys independent
        mac_key = hmac.digest(key_bytes, b"MAC-Key-Derivation", hashlib.sha256)

        # Compute HMAC over IV + ciphertext
        mac = hmac.digest(mac_key, iv + ciphertext, hashlib.sha256)

        # Combine Salt, MAC, IV, and ciphertext
        combined = salt + mac + iv + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    @classmethod
    def decrypt(cls, ciphertext_b64: str, key: str) -> str:
        """
        Decrypt a base64-encoded CTR encrypted string after verifying the MAC.
        """
        combined = base64.b64decode(ciphertext_b64.encode("utf-8"))
        if len(combined) < 16 + 32 + 16:
            raise ValueError("Invalid ciphertext: too short for salt, MAC, and IV.")

        salt = combined[:16]
        mac = combined[16:48]
        iv = combined[48:64]
        ciphertext = combined[64:]

        # Strengthen key derivation using PBKDF2 with HMAC-SHA256 and the extracted salt
        key_bytes = hashlib.pbkdf2_hmac("sha256", key.encode("utf-8"), salt, 100000)

        # Derive the distinct MAC key
        mac_key = hmac.digest(key_bytes, b"MAC-Key-Derivation", hashlib.sha256)

        # Verify HMAC before decrypting (Encrypt-then-MAC verification)
        expected_mac = hmac.digest(mac_key, iv + ciphertext, hashlib.sha256)
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Ciphertext verification failed: HMAC mismatch.")

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
        if master_key not in os.environ.values():
            raise ValueError("Master key must be loaded strictly from an OS environment variable.")
        encrypted = self.engine.encrypt(secret_value, master_key)
        self._secrets[name] = encrypted

    def get_secret(self, name: str, master_key: str) -> Optional[str]:
        """
        Decrypts and retrieves a stored secret.
        """
        if master_key not in os.environ.values():
            raise ValueError("Master key must be loaded strictly from an OS environment variable.")
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
