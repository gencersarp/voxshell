import pyaudio
import wave
import os
import threading
import queue
import numpy as np

class AudioPlayer:
    """Manages audio output for the voice agent."""
    def __init__(self, channels=1, rate=22050):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            output=True
        )
        self.queue = queue.Queue()
        self.is_playing = False
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def play(self, audio_bytes):
        """Adds audio bytes to the playback queue."""
        self.queue.put(audio_bytes)

    def _process_queue(self):
        while True:
            audio_bytes = self.queue.get()
            self.is_playing = True
            self.stream.write(audio_bytes)
            self.is_playing = False
            self.queue.task_done()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class VoiceEngine:
    """Wraps TTS and STT capabilities."""
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.tts = None
        self.stt = None
        self.player = AudioPlayer()

    def initialize_tts(self, voice_name="en_US-lessac-medium"):
        """Downloads and loads the Piper TTS model."""
        model_path, config_path = self.model_manager.get_tts_model(voice_name)
        from piper import PiperVoice
        self.tts = PiperVoice.load(model_path, config_path)

    def speak(self, text):
        """Converts text to speech and plays it."""
        if not self.tts:
            self.initialize_tts()
        
        # Generate audio and send to player
        import io
        audio_stream = io.BytesIO()
        self.tts.synthesize(text, audio_stream)
        self.player.play(audio_stream.getvalue())

    def listen(self, duration=5):
        """Record audio and convert to text using Whisper."""
        # TODO: Implement Whisper STT
        pass
