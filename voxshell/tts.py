"""
tts.py — lightweight, non-blocking TTS engine.

Primary:  macOS `say` command  (instant, neural voices, no downloads).
Fallback: prints to stderr  (extend with Piper if needed on other platforms).
"""

import platform
import queue
import subprocess
import sys
import threading
from typing import Optional


class SystemTTS:
    """Enqueue text and speak it asynchronously in a background thread."""

    def __init__(self, voice: Optional[str] = None) -> None:
        self._os = platform.system()
        self._voice = voice  # None → OS default
        self._queue: queue.Queue[str] = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def speak(self, text: str) -> None:
        """Enqueue *text* for asynchronous playback. Returns immediately."""
        text = text.strip()
        if text:
            self._queue.put(text)

    def wait_until_done(self) -> None:
        """Block until every enqueued utterance has finished playing."""
        self._queue.join()

    def is_busy(self) -> bool:
        """True if there is speech still queued or playing."""
        return not self._queue.empty()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _worker(self) -> None:
        while True:
            text = self._queue.get()
            try:
                self._say(text)
            except Exception:
                pass
            finally:
                self._queue.task_done()

    def _say(self, text: str) -> None:
        if self._os == 'Darwin':
            cmd = ['say']
            if self._voice:
                cmd += ['-v', self._voice]
            cmd.append(text)
            subprocess.run(cmd, capture_output=True)
        else:
            # Non-macOS: print to stderr so it doesn't corrupt the PTY output
            print(f'\n[VoxShell] {text}\n', file=sys.stderr, flush=True)
