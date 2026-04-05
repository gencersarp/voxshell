import ollama
import os
from typing import Optional

class Summarizer:
    """Summarizes CLI output for voice consumption using local LLMs."""
    
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    # Lines kept from the head and tail when truncating long output.
    _TRUNCATE_HEAD = 30
    _TRUNCATE_TAIL = 10

    def _truncate_output(self, text: str) -> str:
        """Keep the first and last N lines of long output so the LLM sees
        the most informative parts without hitting context limits."""
        lines = text.splitlines()
        total = len(lines)
        cutoff = self._TRUNCATE_HEAD + self._TRUNCATE_TAIL
        if total <= cutoff:
            return text
        omitted = total - cutoff
        head = "\n".join(lines[:self._TRUNCATE_HEAD])
        tail = "\n".join(lines[-self._TRUNCATE_TAIL:])
        return f"{head}\n... [{omitted} lines omitted] ...\n{tail}"

    def summarize(self, text: str) -> str:
        """Attempts to summarize text using Ollama with improved prompting."""
        if not text.strip():
            return "The command returned no output."

        try:
            prompt = (
                "You are VoxShell, a voice-enabled CLI assistant. "
                "The following is the output of a terminal command. "
                "Synthesize this output into a concise, high-signal summary "
                "that is easy to understand when spoken aloud. "
                "Keep it under 25 words. Do not use markdown or special characters.\n\n"
                f"Command Output:\n{self._truncate_output(text)}"
            )
            
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': 'You provide concise, spoken-word summaries of CLI output.'},
                {'role': 'user', 'content': prompt}
            ])
            
            summary = response['message']['content'].strip()
            return summary if summary else self._simple_fallback(text)
            
        except Exception as e:
            # Silent fallback to heuristic
            return self._simple_fallback(text)

    def _simple_fallback(self, text: str) -> str:
        """A robust non-LLM based summarizer."""
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        if not lines:
            return "No content to read."
            
        if len(lines) <= 3:
            return " ".join(lines)
        
        return f"Command finished with {len(lines)} lines of output. The first line was: {lines[0]}"
