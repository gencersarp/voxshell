import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from voxshell.models import ModelManager


class TestBuildVoiceUrl:
    """Unit tests for ModelManager._build_voice_url (was broken before fix)."""

    def setup_method(self):
        self.mm = ModelManager(base_path=tempfile.mkdtemp())
        self.base = self.mm.tts_url

    def test_lessac_medium(self):
        url = self.mm._build_voice_url("en_US-lessac-medium", "en_US-lessac-medium.onnx")
        assert url == f"{self.base}/en/en_US/lessac/medium/en_US-lessac-medium.onnx"

    def test_config_json(self):
        url = self.mm._build_voice_url("en_US-lessac-medium", "en_US-lessac-medium.onnx.json")
        assert url == f"{self.base}/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

    def test_different_locale_and_quality(self):
        url = self.mm._build_voice_url("de_DE-thorsten-high", "de_DE-thorsten-high.onnx")
        assert url == f"{self.base}/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"

    def test_low_quality(self):
        url = self.mm._build_voice_url("en_GB-alan-low", "en_GB-alan-low.onnx")
        assert url == f"{self.base}/en/en_GB/alan/low/en_GB-alan-low.onnx"

    def test_old_broken_url_would_fail(self):
        """Demonstrate that the pre-fix URL logic was wrong."""
        voice_name = "en_US-lessac-medium"
        # The broken formula:  {url}/{voice_name.split('-')[0]}/{voice_name.replace('-', '/')}/...
        broken_path = f"{voice_name.split('-')[0]}/{voice_name.replace('-', '/')}/{voice_name}.onnx"
        # Broken produces:     en_US/en_US/lessac/medium/en_US-lessac-medium.onnx  (wrong)
        assert broken_path == "en_US/en_US/lessac/medium/en_US-lessac-medium.onnx"

        # Fixed produces the correct path: speaker is its own segment, locale is separate
        url = self.mm._build_voice_url(voice_name, f"{voice_name}.onnx")
        assert "/en/en_US/lessac/medium/" in url


class TestModelManagerDownload:
    """Test that get_tts_model skips download when files already exist."""

    def test_no_download_if_cached(self, tmp_path):
        mm = ModelManager(base_path=tmp_path)
        voice = "en_US-lessac-medium"
        # Pre-create fake model files
        (tmp_path / f"{voice}.onnx").write_bytes(b"fake")
        (tmp_path / f"{voice}.onnx.json").write_bytes(b"{}")

        with patch.object(mm, "_download_file") as mock_dl:
            mm.get_tts_model(voice)
            mock_dl.assert_not_called()
