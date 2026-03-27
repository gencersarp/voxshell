import ollama
import os

class Summarizer:
    """Summarizes CLI output for voice consumption."""
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def summarize(self, text):
        """Attempts to summarize text using Ollama."""
        try:
            prompt = (
                "You are a voice agent. I will give you a CLI command output. "
                "Summarize it into a short, natural-sounding phrase for text-to-speech. "
                "Keep it under 30 words. Focus on the most important results.\n\n"
                f"Output:\n{text}"
            )
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            # Fallback to a simple heuristic
            print(f"Warning: Summarization failed ({e}). Using simple fallback.")
            return self._simple_fallback(text)

    def _simple_fallback(self, text):
        """A simple non-LLM based summarizer."""
        lines = text.strip().split("\n")
        if len(lines) <= 5:
            return text
        
        # Take first 3 and last 2 lines
        summary = lines[:3] + ["...", f"and {len(lines)-5} more lines."]
        return " ".join(summary)
