import os
import json
import logging
from typing import Any, Dict, Optional

# Setup local module logger
logger = logging.getLogger(__name__)


class Config:
    """
    Configuration loader for YasinAI system.
    Supports default dictionary values, file-based loading (JSON), and environment variable overrides.
    """

    def __init__(self, defaults: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Configuration with optional defaults.
        """
        self._config: Dict[str, Any] = {
            "app_name": "YasinAI",
            "version": "1.0.0",
            "environment": "production",
            "debug": False,
            "modules": []
        }
        if defaults:
            self._config.update(defaults)

        self._load_from_env()

    def load_from_file(self, filepath: str) -> bool:
        """
        Load configuration from a JSON file and merge with existing config.
        Environment variables will still override the loaded file config.
        """
        if not os.path.exists(filepath):
            logger.warning(f"Configuration file not found at path: {filepath}")
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, dict):
                    self._config.update(file_data)
                    self._load_from_env()  # Ensure env overrides are applied on top
                    logger.info(f"Successfully loaded configuration from {filepath}")
                    return True
                else:
                    logger.error(f"Configuration file {filepath} does not contain a valid JSON object.")
        except Exception as e:
            logger.error(f"Error loading configuration from file {filepath}: {e}", exc_info=True)
        return False

    def _load_from_env(self) -> None:
        """
        Override configurations using environment variables prefixed with 'YASINAI_'.
        For example, 'YASINAI_DEBUG' overrides 'debug'.
        """
        prefix = "YASINAI_"
        for key in list(self._config.keys()):
            env_key = f"{prefix}{key.upper()}"
            if env_key in os.environ:
                val = os.environ[env_key]
                current_val = self._config[key]
                if isinstance(current_val, bool):
                    self._config[key] = val.lower() in ("true", "1", "yes")
                elif isinstance(current_val, int):
                    try:
                        self._config[key] = int(val)
                    except ValueError as e:
                        logger.warning(f"Environment variable '{env_key}' value '{val}' could not be cast to int: {e}")
                elif isinstance(current_val, float):
                    try:
                        self._config[key] = float(val)
                    except ValueError as e:
                        logger.warning(f"Environment variable '{env_key}' value '{val}' could not be cast to float: {e}")
                elif isinstance(current_val, list):
                    try:
                        if val.startswith("[") and val.endswith("]"):
                            self._config[key] = json.loads(val)
                        else:
                            self._config[key] = [item.strip() for item in val.split(",") if item.strip()]
                    except Exception as e:
                        logger.warning(f"Environment variable '{env_key}' value '{val}' could not be parsed to list: {e}")
                else:
                    self._config[key] = val

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value by key.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value dynamically.
        """
        self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the entire configuration as a dictionary copy.
        """
        return self._config.copy()
