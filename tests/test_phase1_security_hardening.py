"""Regression tests for Phase 1 security hardening."""

import base64

import pytest

from security_platform.encryption import EncryptionEngine


def test_encryption_uses_aes_gcm_serialization():
    engine = EncryptionEngine()
    key = engine.generate_key()
    ciphertext = engine.encrypt("phase-one secret", key)
    raw = base64.b64decode(ciphertext, validate=True)

    assert len(raw) >= engine.SALT_SIZE + engine.NONCE_SIZE + 16
    assert engine.decrypt(ciphertext, key) == "phase-one secret"


def test_encryption_uses_fresh_salt_and_nonce():
    engine = EncryptionEngine()
    key = engine.generate_key()

    first = base64.b64decode(engine.encrypt("same plaintext", key), validate=True)
    second = base64.b64decode(engine.encrypt("same plaintext", key), validate=True)

    assert first[: engine.SALT_SIZE] != second[: engine.SALT_SIZE]
    first_nonce = first[engine.SALT_SIZE : engine.SALT_SIZE + engine.NONCE_SIZE]
    second_nonce = second[engine.SALT_SIZE : engine.SALT_SIZE + engine.NONCE_SIZE]
    assert first_nonce != second_nonce


def test_encryption_rejects_wrong_key_and_tampering():
    engine = EncryptionEngine()
    key = engine.generate_key()
    ciphertext = engine.encrypt("do not tamper", key)

    with pytest.raises(ValueError, match="verification failed"):
        engine.decrypt(ciphertext, engine.generate_key())

    raw = bytearray(base64.b64decode(ciphertext, validate=True))
    raw[-1] ^= 1
    tampered = base64.b64encode(raw).decode("ascii")

    with pytest.raises(ValueError, match="authentication tag mismatch"):
        engine.decrypt(tampered, key)


def test_encryption_rejects_invalid_ciphertext():
    engine = EncryptionEngine()

    with pytest.raises(ValueError, match="too short"):
        engine.decrypt("YQ==", engine.generate_key())

    with pytest.raises(ValueError, match="Invalid ciphertext encoding"):
        engine.decrypt("not-base64!!!", engine.generate_key())
