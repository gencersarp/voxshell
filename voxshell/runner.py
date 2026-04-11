"""
runner.py — PTY-based agent subprocess runner.

Launches a command inside a pseudo-terminal so the child process behaves
exactly as if it were running in a real terminal (readline, colours, cursor
control all work).  While forwarding every byte of I/O transparently, it
buffers the agent's output and calls *on_response* after each period of
silence, giving the caller a chance to filter and speak a summary.
"""

import os
import pty
import select
import signal
import sys
import termios
import threading
import time
import tty
from typing import Callable, Optional


class AgentRunner:
    """
    Transparent PTY proxy for an AI agent.

    Usage::

        def on_response(raw_output: str) -> None:
            spoken = clean_for_speech(raw_output)
            tts.speak(spoken)

        runner = AgentRunner("claude --permission-mode bypassPermissions",
                             on_response=on_response)
        exit_code = runner.run()

    The *on_response* callback runs in a daemon thread so it never blocks
    the main I/O loop.  Keep it short or fire-and-forget inside it.
    """

    #: Seconds of output silence that marks the end of one agent response.
    QUIET_TIMEOUT: float = 1.5

    def __init__(
        self,
        command: str,
        on_response: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.command = command
        self.on_response = on_response
        self._buf: list[str] = []
        self._last_out: float = 0.0

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self) -> int:
        """
        Start the agent and block until it exits.

        Returns the agent's exit code (0 = success).
        """
        import subprocess

        master_fd, slave_fd = pty.openpty()
        _copy_winsize(sys.stdout.fileno(), slave_fd)

        proc = subprocess.Popen(
            self.command,
            shell=True,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            preexec_fn=os.setsid,  # own process group so Ctrl-C reaches child
        )
        os.close(slave_fd)  # parent doesn't need the slave end

        # Propagate terminal resize events to the child's PTY
        old_winch = signal.signal(
            signal.SIGWINCH,
            lambda *_: _copy_winsize(sys.stdout.fileno(), master_fd),
        )

        # Switch parent stdin to raw mode so every keystroke goes straight
        # to the PTY master without any local processing.
        try:
            old_attrs = termios.tcgetattr(sys.stdin.fileno())
            has_tty = True
        except termios.error:
            old_attrs = None
            has_tty = False

        try:
            if has_tty:
                tty.setraw(sys.stdin.fileno())
            self._io_loop(master_fd, proc)
        finally:
            if has_tty and old_attrs is not None:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_attrs)
            signal.signal(signal.SIGWINCH, old_winch)
            try:
                os.close(master_fd)
            except OSError:
                pass

        # Flush any output that arrived just before the process exited
        if self._buf and self.on_response:
            self._emit()

        proc.wait()
        return proc.returncode or 0

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _io_loop(self, master_fd: int, proc) -> None:
        stdin_fd = sys.stdin.fileno()

        while proc.poll() is None:
            # Wait up to 100 ms for activity on either end
            try:
                r, _, _ = select.select([master_fd, stdin_fd], [], [], 0.1)
            except (ValueError, OSError, select.error):
                break

            # Agent → terminal (and buffer for TTS)
            if master_fd in r:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if data:
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                    self._buf.append(data.decode("utf-8", errors="replace"))
                    self._last_out = time.monotonic()

            # User keyboard → agent
            if stdin_fd in r:
                try:
                    data = os.read(stdin_fd, 4096)
                except OSError:
                    break
                if data:
                    try:
                        os.write(master_fd, data)
                    except OSError:
                        break

            # After QUIET_TIMEOUT seconds of silence, ship buffered output to TTS
            if (
                self._buf
                and self._last_out > 0
                and time.monotonic() - self._last_out > self.QUIET_TIMEOUT
                and self.on_response
            ):
                self._emit()

    def _emit(self) -> None:
        """Ship the current buffer to the on_response callback in a daemon thread."""
        text = "".join(self._buf)
        self._buf.clear()
        self._last_out = 0.0
        if self.on_response and text.strip():
            threading.Thread(target=self.on_response, args=(text,), daemon=True).start()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _copy_winsize(src_fd: int, dst_fd: int) -> None:
    """Copy the terminal window size from *src_fd* to *dst_fd*."""
    try:
        import fcntl
        import struct
        buf = fcntl.ioctl(src_fd, termios.TIOCGWINSZ, b"\x00" * 8)
        fcntl.ioctl(dst_fd, termios.TIOCSWINSZ, buf)
    except (OSError, termios.error, AttributeError):
        pass
