import os
import requests
from pathlib import Path


class ModelManager:
    """Handles downloading and selecting local ML model weights."""

    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent / "models"
        else:
            self.base_path = Path(base_path)

        self.base_path.mkdir(parents=True, exist_ok=True)
        self.tts_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

    def _build_voice_url(self, voice_name: str, filename: str) -> str:
        """Build the correct HuggingFace URL for a Piper voice file.

        URL format: {base}/{lang}/{locale}/{speaker}/{quality}/{filename}
        Example:    .../en/en_US/lessac/medium/en_US-lessac-medium.onnx
        """
        parts = voice_name.split("-")   # e.g. ['en_US', 'lessac', 'medium']
        locale = parts[0]               # 'en_US'
        lang = locale.split("_")[0].lower()  # 'en'
        speaker = "-".join(parts[1:-1]) # 'lessac' (supports multi-word speakers)
        quality = parts[-1]             # 'medium'
        return f"{self.tts_url}/{lang}/{locale}/{speaker}/{quality}/{filename}"

    def get_tts_model(self, voice_name="en_US-lessac-medium"):
        """Ensures the Piper model files exist and returns their paths."""
        model_path = self.base_path / f"{voice_name}.onnx"
        config_path = self.base_path / f"{voice_name}.onnx.json"

        if not model_path.exists():
            print(f"Downloading TTS model: {voice_name}...")
            self._download_file(
                self._build_voice_url(voice_name, f"{voice_name}.onnx"),
                model_path,
            )

        if not config_path.exists():
            print(f"Downloading TTS config: {voice_name}...")
            self._download_file(
                self._build_voice_url(voice_name, f"{voice_name}.onnx.json"),
                config_path,
            )

        return str(model_path), str(config_path)

    def get_stt_model(self, model_size="base"):
        """Returns the Whisper model name. faster-whisper downloads automatically."""
        return model_size

    def _download_file(self, url, dest_path):
        """Download a file with a simple progress indicator."""
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    kb_done = downloaded // 1024
                    kb_total = total // 1024
                    print(f"\r  {pct:3d}%  {kb_done}KB / {kb_total}KB", end="", flush=True)

        print(f"\n  Saved: {dest_path.name}")
