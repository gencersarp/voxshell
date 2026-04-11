"""
filter.py — strip technical noise from AI CLI output for text-to-speech.

The goal: given raw terminal output from an AI agent (Claude, Gemini, etc.),
return only the human-readable sentences the agent actually *said* — no code
blocks, no file paths, no URLs, no ANSI escape codes, no markdown syntax.
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Compiled patterns (module-level for performance)
# ---------------------------------------------------------------------------

# ANSI / VT escape sequences
_ANSI = re.compile(
    r'\x1b(?:'
    r'\[[0-9;]*[a-zA-Z]'                    # CSI  e.g. \x1b[32m  \x1b[2J
    r'|\][^\x07\x1b]*(?:\x07|\x1b\\)'      # OSC  e.g. \x1b]0;title\x07
    r'|\([a-zA-Z0-9]|\)[a-zA-Z0-9]'        # G0/G1 charset designation
    r'|[a-zA-Z]'                            # 2-char sequences  e.g. \x1bM
    r')'
)

# Fenced code blocks  (``` … ```)
_CODE_FENCE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
# Indented code (4+ spaces at line start — Markdown style)
_CODE_INDENT = re.compile(r'^    .+$', re.MULTILINE)
# Inline code  (`…`)
_INLINE_CODE = re.compile(r'`[^`\n]{1,200}`')

# URLs
_URL = re.compile(r'https?://\S+|www\.\S+')

# Unix/Mac file paths  (/foo/bar  ~/foo  ../foo)
_FILE_PATH = re.compile(r'(?:^|(?<=\s))(?:~|\.\.?)?/[^\s,;:\'"<>()\[\]]{2,}')
# Windows paths  (C:\foo\bar)
_WIN_PATH = re.compile(r'[A-Za-z]:\\[^\s]+')

# Markdown headers (strip # markers, keep text)
_MD_HEADER = re.compile(r'^#{1,6}\s+', re.MULTILINE)
# Bold / italic markers (keep inner text)
_MD_EMPHASIS = re.compile(r'\*{1,3}([^*\n]+?)\*{1,3}')
_MD_UNDERLINE = re.compile(r'_{1,2}([^_\n]+?)_{1,2}')
# Markdown links → keep label text
_MD_LINK = re.compile(r'\[([^\]]+)\]\([^\)]*\)')
# Markdown images → remove entirely
_MD_IMAGE = re.compile(r'!\[[^\]]*\]\([^\)]*\)')
# Horizontal rules  (---, ===, ***)
_MD_HR = re.compile(r'^[-=*_]{3,}\s*$', re.MULTILINE)

# XML / tool-call tags  (<tool_use>…</tool_use>)
_XML_BLOCK = re.compile(r'<[a-zA-Z_][^>]*>[\s\S]*?</[a-zA-Z_][^>]*>', re.MULTILINE)
_XML_SELF = re.compile(r'<[a-zA-Z_][^>]*/>')

# Line-start characters that indicate non-prose content
_BAD_LINE_START = re.compile(r'^[+\-|>$%\\{}[\]()\d#@]')

# Sentence boundary split
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def clean_for_speech(text: str, max_sentences: int = 3) -> str:
    """Return speakable text extracted from *text*.

    Strips ANSI codes, code blocks, file paths, URLs, markdown syntax, and
    lines that look like shell/code output.  Returns up to *max_sentences*
    clean English sentences, or an empty string if nothing survives.
    """
    if not text:
        return ''

    # Collapse carriage-return overwrites (progress bars, spinners)
    text = re.sub(r'[^\n]*\r(?!\n)', '', text)

    # Strip ANSI escape sequences
    text = _ANSI.sub('', text)

    # Strip XML tool-call blocks
    text = _XML_BLOCK.sub(' ', text)
    text = _XML_SELF.sub('', text)

    # Strip code (fenced before indented, both before inline)
    text = _CODE_FENCE.sub(' ', text)
    text = _CODE_INDENT.sub('', text)
    text = _INLINE_CODE.sub('', text)

    # Markdown: images before links
    text = _MD_IMAGE.sub('', text)
    text = _MD_LINK.sub(r'\1', text)

    # URLs and paths
    text = _URL.sub('', text)
    text = _FILE_PATH.sub('', text)
    text = _WIN_PATH.sub('', text)

    # Markdown structure (keep readable text)
    text = _MD_HEADER.sub('', text)
    text = _MD_EMPHASIS.sub(r'\1', text)
    text = _MD_UNDERLINE.sub(r'\1', text)
    text = _MD_HR.sub('', text)

    # Process line by line
    prose: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Skip lines that start with non-prose characters
        if _BAD_LINE_START.match(line):
            continue

        # Strip list markers but keep the sentence
        line = re.sub(r'^[-•*]\s+', '', line)
        line = re.sub(r'^\d+\.\s+', '', line).strip()
        if not line:
            continue

        # Skip lines that are predominantly non-alphabetic (< 45 % letters)
        alpha = sum(c.isalpha() for c in line)
        if alpha / len(line) < 0.45:
            continue

        # Skip very short fragments
        if len(line) < 8:
            continue

        prose.append(line)

    if not prose:
        return ''

    joined = ' '.join(prose)

    # Take the first N sentences
    sentences = _SENTENCE_SPLIT.split(joined)
    result = ' '.join(sentences[:max_sentences])

    # Final cleanup
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\s+[,;:]\s*$', '', result)

    return result
