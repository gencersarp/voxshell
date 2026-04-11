import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages persistent user configuration for VoxShell."""

    def __init__(self):
        self.config_path = Path.home() / ".voxshell.json"
        self.defaults: Dict[str, Any] = {
            "voice": "en_US-lessac-medium",
            "llm_model": "llama3",
            "friendly_mode": False,
            "say_voice": "Samantha",   # macOS `say` voice for agent runner
            "agents": {},              # {name: command}
        }
        self.config = self._load_config()

    # ------------------------------------------------------------------
    # General config
    # ------------------------------------------------------------------

    def get(self, key: str) -> Any:
        return self.config.get(key, self.defaults.get(key))

    def save_config(self, new_config: Dict[str, Any]) -> None:
        self.config.update(new_config)
        self._persist()

    def reset_to_defaults(self) -> None:
        self.config = dict(self.defaults)
        self._persist()

    # ------------------------------------------------------------------
    # Agent registry
    # ------------------------------------------------------------------

    def get_agents(self) -> Dict[str, str]:
        """Return all registered agents as {name: command}."""
        return dict(self.config.get("agents", {}))

    def add_agent(self, name: str, command: str) -> None:
        """Add or update an agent entry."""
        agents = self.get_agents()
        agents[name] = command
        self.config["agents"] = agents
        self._persist()

    def remove_agent(self, name: str) -> bool:
        """Remove an agent by name. Returns True if it existed."""
        agents = self.get_agents()
        if name not in agents:
            return False
        del agents[name]
        self.config["agents"] = agents
        self._persist()
        return True

    def get_agent(self, name: str) -> Optional[str]:
        """Return the command for agent *name*, or None if not found."""
        return self.get_agents().get(name)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return dict(self.defaults)
        try:
            with open(self.config_path, "r") as f:
                saved = json.load(f)
            # Merge: saved values win, but defaults fill missing keys
            merged = dict(self.defaults)
            merged.update(saved)
            # Ensure nested "agents" dict is always present
            if not isinstance(merged.get("agents"), dict):
                merged["agents"] = {}
            return merged
        except Exception:
            return dict(self.defaults)

    def _persist(self) -> None:
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)
