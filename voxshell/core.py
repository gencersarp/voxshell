import subprocess
import threading
import sys
import os
from typing import Callable, Optional, Tuple, List

class CommandRunner:
    """Handles execution and real-time output capture of CLI commands."""
    
    def __init__(self, command: str, on_text_callback: Optional[Callable[[str], None]] = None):
        self.command = command
        self.on_text_callback = on_text_callback
        self.process: Optional[subprocess.Popen] = None
        self.output: List[str] = []

    def run(self) -> Tuple[int, str]:
        """Runs the command and captures output in real-time."""
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            if self.process.stdout is None:
                return 1, "Failed to capture stdout"

            for line in iter(self.process.stdout.readline, ""):
                print(line, end="") # Print to terminal in real-time
                self.output.append(line)
                if self.on_text_callback:
                    self.on_text_callback(line)

            self.process.stdout.close()
            return_code = self.process.wait()
            return return_code, "".join(self.output)

        except Exception as e:
            print(f"Error running command: {e}")
            return 1, str(e)

def run_in_background(command: str, callback: Callable[[str], None]) -> Tuple[threading.Thread, CommandRunner]:
    """Utility to run a command and process output via a callback."""
    runner = CommandRunner(command, callback)
    thread = threading.Thread(target=runner.run)
    thread.start()
    return thread, runner
