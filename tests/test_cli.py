import unittest
from click.testing import CliRunner
from voxshell.cli import main
from voxshell.config import ConfigManager
import os
import json
from pathlib import Path

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        # Mock ConfigManager to use a temporary config file
        self.config_patch = Path.home() / ".voxshell.json"
        if self.config_patch.exists():
            self.old_config = self.config_patch.read_text()
        else:
            self.old_config = None

    def tearDown(self):
        # Restore old config
        if self.old_config:
            self.config_patch.write_text(self.old_config)
        elif self.config_patch.exists():
            self.config_patch.unlink()

    def test_alias_command(self):
        result = self.runner.invoke(main, ["alias"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Shell Aliases", result.output)
        self.assertIn("alias vxr='voxshell run'", result.output)

    def test_config_sentences(self):
        # Set max_sentences via config command
        result = self.runner.invoke(main, ["config", "--sentences", "5"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Config updated", result.output)

        # Verify it's saved
        cm = ConfigManager()
        self.assertEqual(cm.get("max_sentences"), 5)

        # Check output of config command
        result = self.runner.invoke(main, ["config"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("max_sentences", result.output)
        self.assertIn("5", result.output)
