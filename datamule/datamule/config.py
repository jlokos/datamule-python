"""Configuration management for datamule.

This module provides configuration persistence for datamule settings,
storing user preferences in a JSON file located at ~/.datamule/config.json.
"""

import json
import os
from typing import Any, Dict, Optional


class Config:
    """Manages datamule configuration settings.

    This class handles loading, saving, and accessing configuration settings
    stored in a JSON file. The configuration file is automatically created
    if it does not exist.

    Attributes:
        config_path: Path to the configuration file (~/.datamule/config.json).
    """

    def __init__(self) -> None:
        """Initialize the Config instance.

        Creates the configuration file and directory if they do not exist.
        """
        self.config_path: str = os.path.expanduser("~/.datamule/config.json")
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Ensure the configuration file and directory exist.

        Creates the ~/.datamule directory and config.json file if they
        do not already exist. Initializes with default settings.
        """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            self._save_config({"default_source": None})

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to the JSON file.

        Args:
            config: Dictionary containing configuration settings to save.
        """
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def set_default_source(self, source: Optional[str]) -> None:
        """Set the default data source.

        Args:
            source: The data source identifier to set as default,
                or None to clear the default.
        """
        config = self._load_config()
        config["default_source"] = source
        self._save_config(config)

    def get_default_source(self) -> Optional[str]:
        """Get the current default data source.

        Returns:
            The default data source identifier, or None if not set.
        """
        config = self._load_config()
        return config.get("default_source")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from the JSON file.

        Returns:
            Dictionary containing the current configuration settings.
        """
        with open(self.config_path) as f:
            return json.load(f)