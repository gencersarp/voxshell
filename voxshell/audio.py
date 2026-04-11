import io
import os
import queue
import tempfile
import threading
import wave

import pyaudio


class AudioPlayer:
    """Manages non-blocking audio output via a background playback thread."""

    def __init__(self, channels: int = 1, rate: int = 22050):
        self.channels = channels
        self.rate = rate
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            output=True,
        )
        self._queue: queue.Queue = queue.Queue()
        self.is_playing = False
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def play(self, pcm_bytes: bytes) -> None:
        """Enqueue raw 16-bit PCM bytes for playback."""
        self._queue.put(pcm_bytes)

    def _process_queue(self) -> None:
        while True:
            pcm_bytes = self._queue.get()
            self.is_playing = True
            self._stream.write(pcm_bytes)
            self.is_playing = False
            self._queue.task_done()

    def wait_until_done(self) -> None:
        """Block until all enqueued audio has finished playing."""
        self._queue.join()

    def close(self) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()


class VoiceEngine:
    """Wraps TTS (Piper) and STT (Whisper) capabilities."""

    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.tts = None
        self.stt = None
        self.player: AudioPlayer | None = None

    # ------------------------------------------------------------------
    # TTS
    # ------------------------------------------------------------------

    def initialize_tts(self, voice_name: str = "en_US-lessac-medium") -> None:
        """Download (if needed) and load the Piper TTS model."""
        model_path, config_path = self.model_manager.get_tts_model(voice_name)
        from piper import PiperVoice

        self.tts = PiperVoice.load(model_path, config_path)

        # Re-create AudioPlayer with the model's actual sample rate.
        sample_rate = self.tts.config.sample_rate
        if self.player is not None:
            self.player.close()
        self.player = AudioPlayer(channels=1, rate=sample_rate)

    def speak(self, text: str) -> None:
        """Convert *text* to speech and enqueue it for playback.

        Uses PiperVoice.synthesize() which yields AudioChunk objects
        containing raw int16 PCM — no WAV header stripping needed.
        """
        if not self.tts:
            self.initialize_tts()

        pcm_chunks = b"".join(
            chunk.audio_int16_bytes for chunk in self.tts.synthesize(text)
        )
        self.player.play(pcm_chunks)

    # ------------------------------------------------------------------
    # STT
    # ------------------------------------------------------------------

    def initialize_stt(self, model_size: str = "base") -> None:
        """Load the faster-whisper model for speech recognition."""
        from faster_whisper import WhisperModel

        model_name = self.model_manager.get_stt_model(model_size)
        print(f"Loading STT model ({model_size})...")
        self.stt = WhisperModel(model_name, device="cpu", compute_type="int8")

    def listen(self, duration: int = 5, stt_model: str = "base") -> str:
        """Record *duration* seconds of microphone audio and return transcribed text.

        Records at 16 kHz mono (required by Whisper) using a separate PyAudio
        instance so it does not conflict with the playback stream.
        """
        if self.stt is None:
            self.initialize_stt(stt_model)

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16_000  # Whisper expects 16 kHz

        p = pyaudio.PyAudio()
        sample_width = p.get_sample_size(FORMAT)
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print(f"  Listening for {duration}s... (speak now)", flush=True)
        frames = []
        for _ in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Write frames to a temporary WAV file — faster-whisper accepts BinaryIO
        # but a real file path is safest across versions.
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
        wav_buffer.seek(0)

        segments, _ = self.stt.transcribe(wav_buffer, beam_size=5)
        return " ".join(seg.text for seg in segments).strip()
