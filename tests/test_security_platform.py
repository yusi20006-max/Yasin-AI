"""
Unit Tests for YasinAI Security Platform.
Covers Identity, Authentication, Authorization, Encryption, and Monitoring.
"""

import time
import pytest
from security_platform.identity import IdentityManager
from security_platform.auth import AuthManager
from security_platform.authorization import PolicyEngine
from security_platform.encryption import EncryptionEngine, SecretStore
from security_platform.monitoring import AuditLogger, ThreatDetector


# --- Identity Tests ---

def test_identity_manager_create_and_delete_role():
    id_mgr = IdentityManager()

    role = id_mgr.create_role("admin", "Administrator privileges")
    assert role.name == "admin"
    assert role.description == "Administrator privileges"

    # Assert duplicates raise exception
    with pytest.raises(ValueError):
        id_mgr.create_role("admin")

    assert id_mgr.get_role("admin") is role
    assert id_mgr.get_role("nonexistent") is None

    assert id_mgr.delete_role("admin") is True
    assert id_mgr.get_role("admin") is None
    assert id_mgr.delete_role("nonexistent") is False


def test_identity_manager_user_roles():
    id_mgr = IdentityManager()
    id_mgr.create_role("member", "Normal member")
    id_mgr.create_role("moderator", "Can moderate")

    user = id_mgr.create_user("alice", roles=["member"])
    assert user.username == "alice"
    assert user.has_role("member") is True
    assert user.has_role("moderator") is False

    # Try creating with invalid role
    with pytest.raises(ValueError):
        id_mgr.create_user("bob", roles=["invalid_role"])

    # Try creating duplicate user
    with pytest.raises(ValueError):
        id_mgr.create_user("alice")

    # Assign and revoke roles
    assert id_mgr.assign_role_to_user("alice", "moderator") is True
    assert user.has_role("moderator") is True

    assert id_mgr.revoke_role_from_user("alice", "member") is True
    assert user.has_role("member") is False
    assert user.has_role("moderator") is True

    # Revoke nonexistent role
    assert id_mgr.revoke_role_from_user("alice", "nonexistent") is False


# --- Authentication Tests ---

def test_auth_manager_lifecycle():
    id_mgr = IdentityManager()
    id_mgr.create_role("user")
    id_mgr.create_user("bob", roles=["user"])

    auth_mgr = AuthManager(id_mgr)

    # Register password
    auth_mgr.register_credentials("bob", "secret_pass_123")

    # Correct credentials login
    token = auth_mgr.login("bob", "secret_pass_123")
    assert token is not None
    assert auth_mgr.validate_token(token) is True

    session = auth_mgr.get_session(token)
    assert session is not None
    assert session.username == "bob"

    # Incorrect credentials login
    assert auth_mgr.login("bob", "wrong_pass") is None

    # Inactive user login
    user = id_mgr.get_user("bob")
    user.active = False
    assert auth_mgr.login("bob", "secret_pass_123") is None
    # Token should now fail validation because user is inactive
    assert auth_mgr.validate_token(token) is False

    # Logout
    user.active = True
    valid_token = auth_mgr.login("bob", "secret_pass_123")
    assert auth_mgr.validate_token(valid_token) is True
    assert auth_mgr.logout(valid_token) is True
    assert auth_mgr.validate_token(valid_token) is False


def test_session_expiration():
    id_mgr = IdentityManager()
    id_mgr.create_role("user")
    id_mgr.create_user("charlie", roles=["user"])

    auth_mgr = AuthManager(id_mgr)
    auth_mgr.register_credentials("charlie", "password")

    # Short duration session
    token = auth_mgr.login("charlie", "password", session_duration=-5)
    # Token should be expired immediately
    assert auth_mgr.validate_token(token) is False


# --- Authorization Tests ---

def test_policy_engine_authorization():
    id_mgr = IdentityManager()
    id_mgr.create_role("admin")
    id_mgr.create_role("guest")
    id_mgr.create_user("super_user", roles=["admin"])
    id_mgr.create_user("visitor", roles=["guest"])

    policy_engine = PolicyEngine(id_mgr)

    # Create permissions
    read_perm = policy_engine.create_permission("data:read", "Read access to database")
    write_perm = policy_engine.create_permission("data:write", "Write access to database")

    # Create policy
    policy_engine.create_policy("AdminAccess", ["admin"], ["data:read", "data:write"])
    policy_engine.create_policy("GuestAccess", ["guest"], ["data:read"])

    # Test permissions
    assert policy_engine.is_authorized("super_user", "data:read") is True
    assert policy_engine.is_authorized("super_user", "data:write") is True

    assert policy_engine.is_authorized("visitor", "data:read") is True
    assert policy_engine.is_authorized("visitor", "data:write") is False

    # Non-existent user/permission checks
    assert policy_engine.is_authorized("nonexistent", "data:read") is False
    assert policy_engine.is_authorized("super_user", "data:nonexistent") is False


# --- Encryption Tests ---

def test_encryption_engine():
    engine = EncryptionEngine()

    key = engine.generate_key()
    assert len(key) == 64  # Hex key of 32 bytes

    plaintext = "Sensitive YasinAI context and long term memories."
    ciphertext = engine.encrypt(plaintext, key)
    assert ciphertext != plaintext

    decrypted = engine.decrypt(ciphertext, key)
    assert decrypted == plaintext

    # Different key should fail decryption
    another_key = engine.generate_key()
    with pytest.raises(Exception):
        engine.decrypt(ciphertext, another_key)


def test_encryption_engine_tampering():
    engine = EncryptionEngine()
    key = engine.generate_key()
    plaintext = "Top secret information."
    ciphertext_b64 = engine.encrypt(plaintext, key)

    # Let's decode to modify a byte in the encrypted combined data
    import base64
    combined = bytearray(base64.b64decode(ciphertext_b64.encode("utf-8")))

    # Flip the last bit of the last byte to tamper with it
    combined[-1] ^= 1

    tampered_ciphertext = base64.b64encode(combined).decode("utf-8")

    # Decryption should fail due to MAC verification failure (HMAC mismatch)
    with pytest.raises(ValueError, match="HMAC mismatch"):
        engine.decrypt(tampered_ciphertext, key)


def test_secret_store(monkeypatch):
    engine = EncryptionEngine()
    store = SecretStore(engine)

    master_key = "secure_master_password"
    # Ensure master_key is set in environment so SecretStore permits it
    monkeypatch.setenv("YASINAI_MASTER_KEY", master_key)

    store.set_secret("DATABASE_URL", "postgresql://db_user:password@localhost/yasin", master_key)
    store.set_secret("OPENAI_API_KEY", "sk-proj-12345abcdef", master_key)

    assert "DATABASE_URL" in store.list_secrets()
    assert "OPENAI_API_KEY" in store.list_secrets()

    # Successful retrieval
    assert store.get_secret("DATABASE_URL", master_key) == "postgresql://db_user:password@localhost/yasin"
    assert store.get_secret("OPENAI_API_KEY", master_key) == "sk-proj-12345abcdef"

    # Failed retrieval with wrong master key
    with pytest.raises(ValueError, match="Master key must be loaded strictly from an OS environment variable"):
        store.get_secret("DATABASE_URL", "wrong_master_password")

    # Delete secret
    assert store.delete_secret("DATABASE_URL") is True
    assert "DATABASE_URL" not in store.list_secrets()
    assert store.get_secret("DATABASE_URL", master_key) is None


# --- Monitoring and Threat Detection Tests ---

def test_monitoring_audit_and_threats():
    logger = AuditLogger()
    detector = ThreatDetector(logger)

    # Low severity normal login logs
    logger.log_event("login", "alice", "success", "Successful login", "low")
    logger.log_event("login", "bob", "success", "Successful login", "low")

    assert len(logger.get_logs()) == 2
    assert len(logger.get_logs(username="alice")) == 1
    assert len(logger.get_logs(event_type="login")) == 2

    # Clear logs
    logger.clear()
    assert len(logger.get_logs()) == 0

    # 1. Threat Detection: Brute Force Login Attack
    logger.log_event("login", "eve", "failure", "Failed login password attempt 1", "medium")
    logger.log_event("login", "eve", "failure", "Failed login password attempt 2", "medium")
    logger.log_event("login", "eve", "failure", "Failed login password attempt 3", "high")

    threats = detector.detect_threats()
    brute_force_threats = [t for t in threats if t["type"] == "BruteForceAttack"]
    assert len(brute_force_threats) >= 1
    assert brute_force_threats[0]["username"] == "eve"
    assert brute_force_threats[0]["severity"] == "critical"

    # 2. Threat Detection: Privilege Abuse
    logger.log_event("authorization", "eve", "failure", "Unauthorized call to system admin API", "high")
    logger.log_event("authorization", "eve", "failure", "Unauthorized call to developer shell API", "high")
    logger.log_event("authorization", "eve", "failure", "Unauthorized call to encryption master key", "critical")

    threats = detector.detect_threats()
    privilege_threats = [t for t in threats if t["type"] == "PrivilegeAbuse"]
    assert len(privilege_threats) >= 1
    assert privilege_threats[0]["username"] == "eve"
    assert privilege_threats[0]["severity"] == "medium"

    # 3. Threat Detection: Access attempt by inactive user
    logger.log_event("authorization", "deleted_user", "failure", "Attempted access by a disabled user profile", "high")
    threats = detector.detect_threats()
    inactive_threats = [t for t in threats if t["type"] == "InactiveUserAccessAttempt"]
    assert len(inactive_threats) >= 1
    assert inactive_threats[0]["username"] == "deleted_user"
    assert inactive_threats[0]["severity"] == "high"


def test_login_timing_mitigation(monkeypatch):
    id_mgr = IdentityManager()
    id_mgr.create_role("user")
    id_mgr.create_user("bob", roles=["user"])

    auth_mgr = AuthManager(id_mgr)
    auth_mgr.register_credentials("bob", "secret_pass_123")

    # Record the arguments of pbkdf2_hmac calls
    pbkdf2_calls = []
    import hashlib
    original_pbkdf2 = hashlib.pbkdf2_hmac

    def mock_pbkdf2(*args, **kwargs):
        pbkdf2_calls.append(args)
        return original_pbkdf2(*args, **kwargs)

    monkeypatch.setattr(hashlib, "pbkdf2_hmac", mock_pbkdf2)

    # 1. Login with nonexistent user - should still call PBKDF2 to prevent timing attacks
    res = auth_mgr.login("nonexistent", "some_password")
    assert res is None
    assert len(pbkdf2_calls) == 1
    assert pbkdf2_calls[0][3] == 600000  # 600,000 iterations

    pbkdf2_calls.clear()

    # 2. Login with registered inactive user - should still call PBKDF2
    user = id_mgr.get_user("bob")
    user.active = False
    res = auth_mgr.login("bob", "secret_pass_123")
    assert res is None
    assert len(pbkdf2_calls) == 1
    assert pbkdf2_calls[0][3] == 600000

    pbkdf2_calls.clear()

    # 3. Login with active user, wrong password - should call PBKDF2
    user.active = True
    res = auth_mgr.login("bob", "wrong_password")
    assert res is None
    assert len(pbkdf2_calls) == 1
    assert pbkdf2_calls[0][3] == 600000
