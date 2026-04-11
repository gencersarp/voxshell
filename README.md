<div align="center">

```
 _   _           ___ _        _ _
| | | |_____ __ / __| |_  ___| | |
| |_| / _ \ \ / \__ \ ' \/ -_) | |
 \___/\___/_\_\ |___/_||_\___|_|_|
```

**A voice layer for AI agents — 100 % local, no cloud.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-46%20passing-success.svg)](#)

</div>

---

VoxShell wraps any AI CLI tool (Claude, Gemini, GPT-shell, …) and gives it a voice.
You see the full raw output. VoxShell quietly speaks a clean summary after each
response — stripping code blocks, file paths, URLs, and markdown so you only
hear what the AI actually *said*.

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│  Agent registry                                         │
│    claude  →  "claude --permission-mode bypassPerm…"    │
│    gemini  →  "gemini"                                  │
│                                                         │
│  voxshell run claude                                    │
│        │                                                │
│        ▼                                                │
│  PTY subprocess  ──►  your terminal  (full output)      │
│        │                                                │
│        ▼  (after 1.5 s of silence)                      │
│  Output filter                                          │
│    strip: ANSI, code blocks, paths, URLs, markdown      │
│    keep:  readable English sentences                    │
│        │                                                │
│        ▼                                                │
│  macOS `say`  →  spoken summary                        │
│                                                         │
│  You type  →  agent stdin  (normal interaction)         │
└─────────────────────────────────────────────────────────┘
```

---

## Quick start

```bash
git clone https://github.com/gencersarp/voxshell.git
cd voxshell
pip install -e .
```

**Register your agents:**

```bash
voxshell agents add claude "claude --permission-mode bypassPermissions"
voxshell agents add gemini "gemini"
```

**Run one:**

```bash
voxshell run claude
```

The agent starts normally in your terminal. After each response, VoxShell
speaks a short summary via the macOS `say` command. You type as usual — your
input goes straight to the agent.

---

## Commands

### Agent management

```bash
voxshell agents list                       # show all registered agents
voxshell agents add <name> "<command>"     # add or update
voxshell agents remove <name>             # remove
```

### Running an agent

```bash
voxshell run <agent>                  # run with voice summaries
voxshell run <agent> --no-voice       # run silently (text only)
voxshell run <agent> --voice Ava      # use a different macOS voice
voxshell run <agent> --sentences 5    # speak up to 5 sentences per response
```

### Config

```bash
voxshell config                        # show current settings
voxshell config --say-voice Ava        # change the default macOS voice
```

Available macOS voices: `say -v ?`  Good options: `Samantha`, `Ava`, `Tom`, `Alex`.

---

## Output filter

After each agent response, VoxShell strips:

| Removed | Kept |
|---------|------|
| Fenced and inline code blocks | Prose sentences |
| File paths (`/path/to/file`, `~/…`) | List items rewritten as sentences |
| URLs | Markdown headers (text only) |
| ANSI escape codes | Bold / italic text (markers stripped) |
| XML tool-call tags | First N sentences (configurable) |
| Lines with < 45 % alphabetic content | |
| Progress bars / spinner overwrites | |

---

## Other modes

VoxShell also supports wrapping arbitrary shell commands:

```bash
# Speak every line of output as it streams (uses Piper TTS)
voxshell "git log --oneline -10" --full

# Summarize via local LLM then speak (needs Ollama)
voxshell "ls -la /usr/local/bin" --friendly

# Old voice-input shell loop (uses Whisper STT + Piper TTS)
voxshell interact
```

---

## Roadmap

- [x] TTS output for any CLI command
- [x] LLM summarization (`--friendly`)
- [x] Voice command input (`interact`)
- [x] **Agent registry** (add / remove / list)
- [x] **PTY runner** — full terminal passthrough with voice summaries
- [x] **Smart output filter** — strips code, paths, URLs, markdown
- [ ] Silence-detection for `interact` (auto-stop listening)
- [ ] Shell aliases / `.zshrc` helpers
- [ ] Multi-language voices

---

## Contributing

```bash
pip install pytest
pytest tests/ -v   # 46 tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md).  MIT License.

---

<div align="center">
Made by <a href="https://github.com/gencersarp">gencersarp</a>
</div>
