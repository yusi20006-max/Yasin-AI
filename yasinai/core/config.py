"""Configuration loader for YasinAI."""

import os
from typing import Any, Dict


class Configuration:
    """YasinAI Configuration class."""

    def __init__(self, data: Dict[str, Any] = None) -> None:
        """Initialize configuration with a dictionary."""
        self._data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._data[key] = value

    @property
    def data(self) -> Dict[str, Any]:
        """Return the dictionary representation of configuration."""
        return self._data


def load_config(config_path: str = None) -> Configuration:
    """Load configuration from environment variables and optionally a file."""
    config_data: Dict[str, Any] = {}

    # Load from environment variables starting with YASINAI_
    for key, val in os.environ.items():
        if key.startswith("YASINAI_"):
            config_key = key[len("YASINAI_") :].lower()
            config_data[config_key] = val

    # Optionally load from config file if specified and exists
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        config_data[k.strip().lower()] = v.strip()
        except Exception:
            pass

    return Configuration(config_data)
