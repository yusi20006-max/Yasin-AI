import os
import logging
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Type, Union

# Set up logging
logger = logging.getLogger("feedbridge.config")


class ConfigurationError(Exception):
    """Raised when there is an issue loading or parsing configuration."""

    pass


DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "name": "FeedBridge",
        "environment": "production",
    },
    "database": {
        "path": "feedbridge.db",
    },
    "scheduler": {
        "interval": 600,
    },
    "fetch": {
        "interval": 600,
    },
    "ai": {
        "enabled": False,
        "model": "gpt-4o",
        "prompt_template": "Clean and translate the following Telegram post for publication. Content:\n{content}",
    },
    "publish": {
        "eitaa_base_url": "https://eitaa.com/",
    },
    "logging": {
        "level": "INFO",
    },
}


class Config:
    """
    Configuration loader for FeedBridge system.
    Supports default dictionary values, YAML-based loading, and environment variable overrides/secrets.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        env_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize Configuration.
        Loads environment variables from .env first, then default values, then overrides with config.yaml,
        and finally overrides with FEEDBRIDGE_ environment variables.
        """
        # Load environment variables from .env file
        self._load_dotenv_file(env_path)

        # Initialize config dictionary with deep copy of defaults
        self._config = self._deep_copy(DEFAULT_CONFIG)

        # Try to locate and load YAML configuration
        resolved_config_path = self._resolve_config_path(config_path)
        if resolved_config_path:
            self.load_from_yaml(resolved_config_path)
        else:
            logger.info(
                "No config.yaml found; using default settings and environment variables."
            )

        # Apply environment overrides on top of everything
        self._apply_env_overrides()

    def _deep_copy(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a simple deep copy of nested dictionaries."""
        copied: Dict[str, Any] = {}
        for k, v in d.items():
            if isinstance(v, dict):
                copied[k] = self._deep_copy(v)
            elif isinstance(v, list):
                copied[k] = list(v)
            else:
                copied[k] = v
        return copied

    def _load_dotenv_file(self, env_path: Optional[Union[str, Path]]) -> None:
        """Load .env file from the specified path or standard fallback locations."""
        if env_path:
            path = Path(env_path)
            if path.exists():
                logger.info(f"Loading environment from specified .env path: {path}")
                load_dotenv(dotenv_path=path)
            else:
                logger.warning(f"Specified .env file does not exist: {path}")
        else:
            # Check default locations
            cwd_env = Path(".env")
            if cwd_env.exists():
                logger.info("Loading environment from local .env file.")
                load_dotenv(dotenv_path=cwd_env)
            else:
                # Also try parent directories
                load_dotenv()

    def _resolve_config_path(
        self, config_path: Optional[Union[str, Path]]
    ) -> Optional[Path]:
        """Resolves the path to the config.yaml file, checking standard fallbacks if not provided."""
        if config_path:
            path = Path(config_path)
            if path.exists() and path.is_file():
                return path
            raise ConfigurationError(
                f"Specified configuration file not found: {config_path}"
            )

        # Check environment variable
        env_config_path = os.getenv("FEEDBRIDGE_CONFIG_PATH")
        if env_config_path:
            path = Path(env_config_path)
            if path.exists() and path.is_file():
                logger.info(
                    f"Using configuration path from FEEDBRIDGE_CONFIG_PATH env: {path}"
                )
                return path
            logger.warning(
                f"FEEDBRIDGE_CONFIG_PATH specifies a non-existent file: {env_config_path}"
            )

        # Check standard paths
        standard_paths = [
            Path("config.yaml"),
            Path("config/config.yaml"),
            Path("src/feedbridge/config/config.yaml"),
        ]
        for p in standard_paths:
            if p.exists() and p.is_file():
                logger.info(f"Found configuration file at standard path: {p}")
                return p

        return None

    def load_from_yaml(self, filepath: Path) -> bool:
        """Loads configuration from a YAML file and merges it into the active configuration."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    logger.warning(f"Configuration file {filepath} is empty.")
                    return False
                if not isinstance(data, dict):
                    raise ConfigurationError(
                        f"Configuration file {filepath} must contain a dictionary at the root."
                    )

                self._merge_dicts(self._config, data)
                logger.info(f"Successfully loaded configuration from {filepath}")
                return True
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML configuration in {filepath}: {e}")
            raise ConfigurationError(f"YAML parsing error in {filepath}: {e}") from e
        except Exception as e:
            logger.error(f"Failed to read configuration file {filepath}: {e}")
            raise ConfigurationError(
                f"Failed to load config from {filepath}: {e}"
            ) from e

    def _merge_dicts(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merges dictionary values from source into target."""
        for k, v in source.items():
            if k in target and isinstance(target[k], dict) and isinstance(v, dict):
                self._merge_dicts(target[k], v)
            else:
                target[k] = v

    def _apply_env_overrides(self) -> None:
        """
        Scan environment variables starting with FEEDBRIDGE_ and override configuration.
        Matches env variables like FEEDBRIDGE_DATABASE_PATH to config['database']['path'].
        """
        prefix = "FEEDBRIDGE_"
        for env_key, env_val in os.environ.items():
            if not env_key.startswith(prefix) or env_key == "FEEDBRIDGE_CONFIG_PATH":
                continue

            # Process key: remove prefix, split by underscores, lowercase
            clean_key = env_key[len(prefix) :].lower()
            if not clean_key:
                continue

            # We try to match clean_key against the dictionary hierarchy
            # To support variables like FEEDBRIDGE_AI_ENABLED (maps to ai.enabled)
            # and FEEDBRIDGE_DATABASE_PATH (maps to database.path)
            parts = clean_key.split("_")

            # Find the best matching key path
            matched_path = self._match_env_key_to_path(parts, self._config)
            if matched_path:
                # Get the existing value to determine expected type
                curr_val = self._get_by_path(matched_path)
                typed_val = self._cast_value(
                    env_val, type(curr_val) if curr_val is not None else str
                )
                self._set_by_path(matched_path, typed_val)
                logger.debug(
                    f"Applied env override: {env_key} -> {'.'.join(matched_path)} = {typed_val}"
                )

    def _match_env_key_to_path(
        self, parts: List[str], current_dict: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        Given environment variable key parts (e.g., ['ai', 'enabled'] or ['database', 'path']),
        resolves them recursively to a valid path of keys in the current configuration.
        """
        # Direct check: try to find a key that matches the whole string or progressive sub-parts
        # Standard case 1: exact match
        if len(parts) == 1:
            if parts[0] in current_dict:
                return [parts[0]]
            return None

        # Standard case 2: parts[0] is a sub-dictionary. Check if parts[1:] can match inside.
        if parts[0] in current_dict and isinstance(current_dict[parts[0]], dict):
            sub_path = self._match_env_key_to_path(parts[1:], current_dict[parts[0]])
            if sub_path:
                return [parts[0]] + sub_path

        # Case 3: multi-word key in environment containing underscores (e.g., app_name, prompt_template)
        # Try joining parts to see if it matches a key
        for i in range(1, len(parts) + 1):
            candidate_key = "_".join(parts[:i])
            if candidate_key in current_dict:
                if i == len(parts):
                    return [candidate_key]
                elif isinstance(current_dict[candidate_key], dict):
                    sub_path = self._match_env_key_to_path(
                        parts[i:], current_dict[candidate_key]
                    )
                    if sub_path:
                        return [candidate_key] + sub_path

        return None

    def _cast_value(self, val_str: str, target_type: Type) -> Any:
        """Safely casts a string value from an environment variable to the target type."""
        if target_type is bool:
            return val_str.lower() in ("true", "1", "yes", "on")
        if target_type is int:
            try:
                return int(val_str)
            except ValueError:
                return val_str
        if target_type is float:
            try:
                return float(val_str)
            except ValueError:
                return val_str
        return val_str

    def _get_by_path(self, key_path: List[str]) -> Any:
        """Retrieves a nested configuration value by its key path list."""
        curr = self._config
        for k in key_path:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return None
        return curr

    def _set_by_path(self, key_path: List[str], value: Any) -> None:
        """Sets a nested configuration value by its key path list."""
        curr = self._config
        for k in key_path[:-1]:
            curr = curr.setdefault(k, {})
        curr[key_path[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value by key. Supports dot-notation for nested structures
        (e.g., 'database.path', 'ai.enabled').
        """
        if not key:
            return default

        parts = key.split(".")
        curr = self._config
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return default
        return curr

    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a configuration value as a string."""
        val = self.get(key, default)
        return str(val) if val is not None else None

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Retrieves a configuration value as an integer."""
        val = self.get(key, default)
        if val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            logger.warning(f"Configuration value for '{key}' is not an integer: {val}")
            return default

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """Retrieves a configuration value as a boolean."""
        val = self.get(key, default)
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return bool(val)
        return str(val).lower() in ("true", "1", "yes", "on")

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a sensitive configuration value (secret) from environment variables or .env.
        Logs access while hiding/masking the actual value for security.
        """
        # Prioritize exact matching environment variable
        env_val = os.getenv(key)
        if env_val is None:
            # Try prefixed environment variable
            env_val = os.getenv(f"FEEDBRIDGE_{key}")

        val = env_val if env_val is not None else self.get(key, default)

        # Log masked value for auditing
        masked = self._mask_value(val)
        logger.info(f"Retrieved secret '{key}': {masked}")
        return val

    def _mask_value(self, val: Any) -> str:
        """Helper to mask sensitive values so they don't leak into logs."""
        if val is None:
            return "None"
        s = str(val)
        if not s:
            return "Empty"
        if len(s) <= 4:
            return "****"
        return f"{s[:2]}****{s[-2:]}"

    def to_dict(self) -> Dict[str, Any]:
        """Returns a copy of the entire configuration dictionary."""
        return self._deep_copy(self._config)
