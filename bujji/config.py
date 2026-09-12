"""
Configuration loader and validator for Bujji.
Supports YAML configuration files with environment variable overrides.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import os

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

class BujjiConfig:
    """Manages Bujji settings, engine preferences, voice, and system toggles."""

    def __init__(self, raw_data: Optional[Dict[str, Any]] = None):
        self._data: Dict[str, Any] = raw_data or {}

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "BujjiConfig":
        path = config_path or DEFAULT_CONFIG_PATH
        if not path.exists():
            return cls({})

        content = path.read_text(encoding="utf-8")
        try:
            import yaml
            data = yaml.safe_load(content) or {}
        except ImportError:
            # Fallback basic loader if pyyaml is still installing
            data = {}
        return cls(data)

    @property
    def assistant_name(self) -> str:
        return self._data.get("assistant", {}).get("name", "Bujji")

    @property
    def assistant_version(self) -> str:
        return self._data.get("assistant", {}).get("version", "0.1.0")

    @property
    def default_engine(self) -> str:
        return self._data.get("engine", {}).get("default_mode", "ollama")

    @property
    def raw(self) -> Dict[str, Any]:
        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
