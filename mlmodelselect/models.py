import os
import requests
from pathlib import Path

class ModelManager:
    """Handles downloading and selecting local ML model weights."""
    def __init__(self, base_path=None):
        if base_path is None:
            # Default to a models directory in the project root
            self.base_path = Path(__file__).parent.parent / "models"
        else:
            self.base_path = Path(base_path)
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.tts_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

    def get_tts_model(self, voice_name="en_US-lessac-medium"):
        """Ensures the Piper model files exist and returns their paths."""
        model_path = self.base_path / f"{voice_name}.onnx"
        config_path = self.base_path / f"{voice_name}.onnx.json"

        if not model_path.exists():
            print(f"Downloading TTS model: {voice_name}...")
            self._download_file(f"{self.tts_url}/{voice_name.split('-')[0]}/{voice_name.replace('-', '/')}/{voice_name}.onnx", model_path)
        
        if not config_path.exists():
            print(f"Downloading TTS config: {voice_name}...")
            self._download_file(f"{self.tts_url}/{voice_name.split('-')[0]}/{voice_name.replace('-', '/')}/{voice_name}.onnx.json", config_path)

        return str(model_path), str(config_path)

    def get_stt_model(self, model_size="base"):
        """Returns the Whisper model name or path."""
        # Faster-Whisper handles downloading automatically if we provide a name
        return model_size

    def _download_file(self, url, dest_path):
        """Helper to download a file with a progress indicator."""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved: {dest_path}")

# Example usage
# mm = ModelManager()
# mm.get_tts_model()
