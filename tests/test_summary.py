import pytest
from unittest.mock import patch, MagicMock

from voxshell.summary import Summarizer


class TestSummarizerFallback:
    """Tests for the heuristic fallback (no Ollama required)."""

    def setup_method(self):
        self.s = Summarizer()

    def test_empty_input(self):
        assert self.s.summarize("") == "The command returned no output."

    def test_whitespace_only(self):
        assert self.s.summarize("   \n  ") == "The command returned no output."

    def test_single_line(self):
        result = self.s._simple_fallback("hello world")
        assert "hello world" in result

    def test_two_lines(self):
        result = self.s._simple_fallback("line one\nline two")
        assert "line one" in result
        assert "line two" in result

    def test_many_lines_mentions_count(self):
        text = "\n".join(f"line {i}" for i in range(10))
        result = self.s._simple_fallback(text)
        assert "10" in result

    def test_fallback_used_when_ollama_fails(self):
        with patch("ollama.chat", side_effect=Exception("connection refused")):
            result = self.s.summarize("some output")
        # Should not raise; should return the heuristic fallback
        assert isinstance(result, str)
        assert len(result) > 0


class TestSummarizerTruncation:
    def setup_method(self):
        self.s = Summarizer()

    def test_short_output_not_truncated(self):
        text = "\n".join(f"line {i}" for i in range(20))
        assert self.s._truncate_output(text) == text

    def test_long_output_truncated(self):
        text = "\n".join(f"line {i}" for i in range(100))
        result = self.s._truncate_output(text)
        assert "omitted" in result
        assert "line 0" in result      # head kept
        assert "line 99" in result     # tail kept
        assert "line 50" not in result  # middle dropped


class TestSummarizerOllama:
    def test_uses_ollama_response(self):
        mock_response = {"message": {"content": "Build succeeded with no errors."}}
        with patch("ollama.chat", return_value=mock_response) as mock_chat:
            s = Summarizer(model_name="llama3")
            result = s.summarize("make: Nothing to be done for 'all'.")
        assert result == "Build succeeded with no errors."
        mock_chat.assert_called_once()

    def test_falls_back_when_response_empty(self):
        mock_response = {"message": {"content": "  "}}
        with patch("ollama.chat", return_value=mock_response):
            s = Summarizer()
            result = s.summarize("some output")
        assert isinstance(result, str)
        assert len(result) > 0
