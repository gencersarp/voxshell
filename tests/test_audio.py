import io
import wave
import struct
import pytest
from unittest.mock import patch, MagicMock, call

from voxshell.audio import AudioPlayer, VoiceEngine
from voxshell.models import ModelManager


def _make_wav_bytes(sample_rate=22050, n_samples=100) -> bytes:
    """Return a minimal valid WAV buffer with silent samples."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_samples)
    return buf.getvalue()


class TestAudioPlayerQueue:
    """AudioPlayer should enqueue and track playback state without crashing."""

    def test_wait_until_done_returns_immediately_when_empty(self):
        with patch("pyaudio.PyAudio") as MockPA:
            mock_stream = MagicMock()
            MockPA.return_value.open.return_value = mock_stream
            player = AudioPlayer()
            # Queue is empty — should return immediately
            player.wait_until_done()

    def test_play_enqueues_bytes(self):
        with patch("pyaudio.PyAudio") as MockPA:
            MockPA.return_value.open.return_value = MagicMock()
            player = AudioPlayer()
            player.play(b"\x00" * 100)
            # After wait the bytes have been consumed
            player.wait_until_done()


class TestVoiceEngineTTS:
    """VoiceEngine.speak() should use AudioChunk.audio_int16_bytes (no WAV header)."""

    def _make_engine(self):
        mm = MagicMock(spec=ModelManager)
        mm.get_tts_model.return_value = ("/fake/model.onnx", "/fake/model.onnx.json")
        return VoiceEngine(mm)

    def test_speak_calls_player_play_with_pcm(self):
        engine = self._make_engine()

        fake_chunk = MagicMock()
        fake_chunk.audio_int16_bytes = b"\x01\x02" * 50

        fake_tts = MagicMock()
        fake_tts.synthesize.return_value = [fake_chunk]
        fake_tts.config.sample_rate = 22050

        fake_player = MagicMock()
        engine.tts = fake_tts
        engine.player = fake_player

        engine.speak("hello")

        fake_player.play.assert_called_once_with(b"\x01\x02" * 50)

    def test_speak_concatenates_multiple_chunks(self):
        engine = self._make_engine()

        chunks = [MagicMock(audio_int16_bytes=b"\xAA" * 10) for _ in range(3)]
        fake_tts = MagicMock()
        fake_tts.synthesize.return_value = chunks
        fake_tts.config.sample_rate = 22050
        fake_player = MagicMock()

        engine.tts = fake_tts
        engine.player = fake_player

        engine.speak("multi chunk")
        fake_player.play.assert_called_once_with(b"\xAA" * 30)

    def test_initialize_tts_creates_player_with_model_sample_rate(self):
        engine = self._make_engine()

        fake_tts = MagicMock()
        fake_tts.config.sample_rate = 16000

        with patch("voxshell.audio.AudioPlayer") as MockPlayer, \
             patch("voxshell.audio.VoiceEngine.initialize_tts", autospec=True) as mock_init:

            def _side(self_arg, voice_name="en_US-lessac-medium"):
                self_arg.tts = fake_tts
                self_arg.player = MockPlayer(channels=1, rate=fake_tts.config.sample_rate)

            mock_init.side_effect = _side
            engine.initialize_tts()

        MockPlayer.assert_called_with(channels=1, rate=16000)


class TestVoiceEngineSTT:
    """VoiceEngine.listen() should record audio and return transcribed text."""

    def test_listen_returns_transcribed_text(self):
        mm = MagicMock(spec=ModelManager)
        mm.get_stt_model.return_value = "base"
        engine = VoiceEngine(mm)

        fake_segment = MagicMock()
        fake_segment.text = " hello world "
        fake_stt = MagicMock()
        fake_stt.transcribe.return_value = ([fake_segment], MagicMock())
        engine.stt = fake_stt

        mock_stream = MagicMock()
        mock_stream.read.return_value = b"\x00\x00" * 1024

        with patch("pyaudio.PyAudio") as MockPA:
            MockPA.return_value.get_sample_size.return_value = 2
            MockPA.return_value.open.return_value = mock_stream
            result = engine.listen(duration=1)

        assert result == "hello world"

    def test_listen_strips_silence_to_empty_string(self):
        mm = MagicMock(spec=ModelManager)
        mm.get_stt_model.return_value = "base"
        engine = VoiceEngine(mm)

        fake_stt = MagicMock()
        fake_stt.transcribe.return_value = ([], MagicMock())
        engine.stt = fake_stt

        mock_stream = MagicMock()
        mock_stream.read.return_value = b"\x00\x00" * 1024

        with patch("pyaudio.PyAudio") as MockPA:
            MockPA.return_value.get_sample_size.return_value = 2
            MockPA.return_value.open.return_value = mock_stream
            result = engine.listen(duration=1)

        assert result == ""
