"""Regression tests for the AES-256-GCM encryption contract."""

import base64

import pytest

from security_platform.encryption import EncryptionEngine


def test_encryption_uses_expected_serialized_layout() -> None:
    key = EncryptionEngine.generate_key()
    ciphertext = EncryptionEngine.encrypt("secret", key)
    raw = base64.b64decode(ciphertext, validate=True)

    # salt + 96-bit nonce + AES-GCM authentication tag
    assert len(raw) >= EncryptionEngine.SALT_SIZE + EncryptionEngine.NONCE_SIZE + 16
    assert EncryptionEngine.decrypt(ciphertext, key) == "secret"


def test_encryption_is_nondeterministic() -> None:
    key = EncryptionEngine.generate_key()

    first = EncryptionEngine.encrypt("same plaintext", key)
    second = EncryptionEngine.encrypt("same plaintext", key)

    assert first != second
    assert EncryptionEngine.decrypt(first, key) == "same plaintext"
    assert EncryptionEngine.decrypt(second, key) == "same plaintext"


def test_tampering_fails_authentication() -> None:
    key = EncryptionEngine.generate_key()
    raw = bytearray(base64.b64decode(EncryptionEngine.encrypt("secret", key), validate=True))
    raw[-1] ^= 0x01

    tampered = base64.b64encode(raw).decode("ascii")
    with pytest.raises(ValueError, match="authentication tag mismatch"):
        EncryptionEngine.decrypt(tampered, key)


def test_invalid_ciphertext_encoding_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid ciphertext encoding"):
        EncryptionEngine.decrypt("not-base64!!!", EncryptionEngine.generate_key())
