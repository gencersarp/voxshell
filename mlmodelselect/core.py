import subprocess
import threading
import sys
import os

class CommandRunner:
    def __init__(self, command, on_text_callback=None):
        self.command = command
        self.on_text_callback = on_text_callback
        self.process = None
        self.output = []

    def run(self):
        """Runs the command and captures output in real-time."""
        try:
            # Use shell=True for flexibility in command execution
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output line by line
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

def run_in_background(command, callback):
    """Utility to run a command and process output via a callback."""
    runner = CommandRunner(command, callback)
    thread = threading.Thread(target=runner.run)
    thread.start()
    return thread, runner
