import json
import os
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """Manages persistent user configuration for VoxShell."""
    
    def __init__(self):
        self.config_path = Path.home() / ".voxshell.json"
        self.defaults = {
            "voice": "en_US-lessac-medium",
            "llm_model": "llama3",
            "friendly_mode": False
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return self.defaults
        try:
            with open(self.config_path, "r") as f:
                return {**self.defaults, **json.load(f)}
        except Exception:
            return self.defaults

    def save_config(self, new_config: Dict[str, Any]):
        """Saves updated configuration to the home directory."""
        self.config.update(new_config)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str) -> Any:
        return self.config.get(key, self.defaults.get(key))

    def reset_to_defaults(self) -> None:
        """Overwrite saved config with factory defaults and reload in memory."""
        self.config = dict(self.defaults)
        with open(self.config_path, "w") as f:
            json.dump(self.defaults, f, indent=4)
