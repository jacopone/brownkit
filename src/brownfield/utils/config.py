"""Configuration management."""

from pathlib import Path


class Config:
    """Configuration loader."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path
        self.data = {}

    def load(self) -> dict:
        """Load configuration from file."""
        # TODO: Implement TOML loading
        return self.data
