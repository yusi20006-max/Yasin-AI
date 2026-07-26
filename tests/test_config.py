import os
import tempfile
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch
from feedbridge.config import Config, ConfigurationError

@pytest.fixture
def temp_yaml_file():
    """Fixture to create a temporary YAML configuration file."""
    data = {
        "app": {
            "environment": "testing",
        },
        "database": {
            "path": "test_feedbridge.db",
        },
        "scheduler": {
            "interval": 30,
        },
        "ai": {
            "enabled": True,
            "model": "gpt-4-test",
        }
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        yaml.dump(data, f)
        filepath = f.name

    yield Path(filepath)

    if os.path.exists(filepath):
        os.unlink(filepath)

@pytest.fixture
def temp_dotenv_file():
    """Fixture to create a temporary .env file."""
    content = """
# Test Dotenv File
FEEDBRIDGE_EITAA_TOKEN=env-token-123
FEEDBRIDGE_AI_API_KEY=env-key-987
FEEDBRIDGE_SCHEDULER_INTERVAL=45
    """
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".env") as f:
        f.write(content)
        filepath = f.name

    yield Path(filepath)

    if os.path.exists(filepath):
        os.unlink(filepath)

def test_default_config_loading():
    """Test that Config initializes with default values when no file or env exists."""
    # Ensure no environment overrides exist and no YAML config is resolved
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(Config, "_resolve_config_path", return_value=None):
            config = Config(config_path=None)  # should fallback to defaults

            assert config.get("app.name") == "FeedBridge"
            assert config.get("app.environment") == "production"
        assert config.get("database.path") == "feedbridge.db"
        assert config.get("scheduler.interval") == 600
        assert config.get("ai.enabled") is False
        assert config.get("ai.model") == "gpt-4o"
        assert config.get_str("logging.level") == "INFO"

def test_load_from_yaml(temp_yaml_file):
    """Test that Config successfully loads values from a YAML file."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config(config_path=temp_yaml_file)

        assert config.get("app.name") == "FeedBridge"  # retained default
        assert config.get("app.environment") == "testing"  # overridden
        assert config.get("database.path") == "test_feedbridge.db"  # overridden
        assert config.get_int("scheduler.interval") == 30  # overridden
        assert config.get_bool("ai.enabled") is True  # overridden
        assert config.get("ai.model") == "gpt-4-test"  # overridden

def test_load_from_yaml_error():
    """Test that invalid YAML file raises ConfigurationError."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        f.write("invalid: yaml: : content")
        filepath = f.name

    try:
        with pytest.raises(ConfigurationError):
            Config(config_path=filepath)
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

def test_env_overrides(temp_yaml_file):
    """Test that environment variables starting with FEEDBRIDGE_ override yaml config."""
    env_vars = {
        "FEEDBRIDGE_APP_ENVIRONMENT": "staging",
        "FEEDBRIDGE_DATABASE_PATH": "env_override.db",
        "FEEDBRIDGE_SCHEDULER_INTERVAL": "15",
        "FEEDBRIDGE_AI_ENABLED": "true",
    }
    with patch.dict(os.environ, env_vars):
        config = Config(config_path=temp_yaml_file)

        assert config.get_str("app.environment") == "staging"
        assert config.get_str("database.path") == "env_override.db"
        assert config.get_int("scheduler.interval") == 15
        assert config.get_bool("ai.enabled") is True

def test_dotenv_loading(temp_yaml_file, temp_dotenv_file):
    """Test that loading from a specified .env file works correctly."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config(config_path=temp_yaml_file, env_path=temp_dotenv_file)

        # Test env variable overridden by .env
        assert config.get_int("scheduler.interval") == 45

        # Test secrets loading
        assert config.get_secret("EITAA_TOKEN") == "env-token-123"
        assert config.get_secret("AI_API_KEY") == "env-key-987"

def test_get_secret_masking():
    """Test that get_secret retrieves the secret and masks it correctly."""
    with patch.dict(os.environ, {"FEEDBRIDGE_EITAA_TOKEN": "mysecrettoken"}):
        config = Config(config_path=None)

        assert config.get_secret("EITAA_TOKEN") == "mysecrettoken"
        assert config._mask_value("mysecrettoken") == "my****en"
        assert config._mask_value(None) == "None"
        assert config._mask_value("") == "Empty"
        assert config._mask_value("123") == "****"

def test_to_dict():
    """Test converting configuration to dictionary copy."""
    config = Config(config_path=None)
    d = config.to_dict()

    assert isinstance(d, dict)
    assert d["app"]["name"] == "FeedBridge"

    # Mutating dict shouldn't mutate config
    d["app"]["name"] = "Mutated"
    assert config.get("app.name") == "FeedBridge"

def test_get_typed_methods():
    """Test type-specific getter methods."""
    config = Config(config_path=None)

    # Setup some values manually to test conversion
    config._config["test"] = {
        "str_val": "hello",
        "int_val": "123",
        "bool_val": "true",
        "bool_val_false": "false",
        "invalid_int": "abc",
    }

    assert config.get_str("test.str_val") == "hello"
    assert config.get_int("test.int_val") == 123
    assert config.get_bool("test.bool_val") is True
    assert config.get_bool("test.bool_val_false") is False
    assert config.get_int("test.invalid_int", default=999) == 999
    assert config.get_int("test.missing", default=100) == 100
