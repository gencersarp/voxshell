<div align="center">

```
 _   _           ___ _        _ _ 
| | | |_____ __ / __| |_  ___| | |
| |_| / _ \ \ / \__ \ ' \/ -_) | |
 \___/\___/_\_\ |___/_||_\___|_|_|
```

**The voice wrapper for any CLI tool — 100 % local, zero cloud.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![100% Local](https://img.shields.io/badge/AI-100%25%20Local-brightgreen.svg)](#how-it-works)
[![Tests](https://img.shields.io/badge/tests-25%20passing-success.svg)](#)

</div>

---

VoxShell turns any shell command into a spoken conversation.  
Prefix a command with `voxshell` and it reads the output back to you — or enter **interactive mode** and speak your commands out loud.

No cloud APIs. No data leaving your machine. Powered by **Piper TTS**, **Whisper STT**, and **Ollama**.

---

## Features

| | |
|---|---|
| **Plug-and-play** | Works with any CLI tool — `git`, `docker`, `kubectl`, custom scripts. |
| **Full mode** | Streams and reads every line of output as it appears. |
| **Friendly mode** | Pipes output through a local LLM to produce a concise, natural-language summary. |
| **Interactive mode** | Speak a command → it runs → the result is spoken back. Loop until you say *"exit"*. |
| **100 % local** | Piper for TTS, faster-whisper for STT, Ollama for summarization. Nothing leaves your machine. |
| **Auto-managed models** | Voice and Whisper models are downloaded automatically on first use. |

---

## Installation

**1. Clone and install**
```bash
git clone https://github.com/gencersarp/voxshell.git
cd voxshell
pip install -e .
```

**2. (Optional) Install Ollama for Friendly Mode**
```bash
# https://ollama.com
ollama pull llama3
```

> The TTS model (~60 MB) is downloaded automatically on first run. The Whisper `base` STT model is downloaded automatically when you use `interact`.

---

## Usage

### Read a command's output aloud

```bash
# Speak every line as it streams
voxshell "git log --oneline -10" --full

# Let an LLM summarize it first, then speak the summary
voxshell "ls -la /usr/local/bin" --friendly
```

### Interactive voice loop

Speak commands out loud. VoxShell runs them and reads back the result. Say **"exit"** to stop.

```bash
voxshell interact

# With options
voxshell interact --friendly --stt-model small --duration 7
```

```
🎙️  VoxShell interactive mode. Say a shell command, or 'exit' to quit.

  Listening for 5s... (speak now)

🗣️  Heard: echo hello world
🚀 Running: echo hello world
hello world
```

### View or update config

```bash
# Show current settings
voxshell config

# Set defaults
voxshell config --voice en_US-lessac-medium --llm llama3
```

---

## Options

### `voxshell "<command>"` flags

| Flag | Description | Default |
|------|-------------|---------|
| `--full` | Read the entire output aloud line-by-line. | off |
| `--friendly` | Summarize via LLM before speaking. | off |
| `--voice` | Piper voice model name. | `en_US-lessac-medium` |
| `--llm` | Ollama model for Friendly Mode. | `llama3` |

### `voxshell interact` flags

| Flag | Description | Default |
|------|-------------|---------|
| `--duration` | Seconds to record per turn. | `5` |
| `--friendly` | Summarize responses before speaking. | off |
| `--stt-model` | Whisper model: `tiny` / `base` / `small` / `medium`. | `base` |
| `--voice` | Piper voice model name. | from config |
| `--llm` | Ollama model for Friendly Mode. | `llama3` |

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                        VoxShell                         │
│                                                         │
│  Your command ──► subprocess ──► stdout                 │
│                                    │                    │
│              ┌─────────────────────┤                    │
│              │                     │                    │
│         --full mode           --friendly mode           │
│    (stream each line)     (buffer → Ollama → summary)   │
│              │                     │                    │
│              └──────────┬──────────┘                    │
│                         │                               │
│                    Piper TTS                            │
│                  (local, offline)                       │
│                         │                               │
│                    PyAudio output                       │
│                                                         │
│  interact mode adds:                                    │
│    Microphone ──► PyAudio ──► Whisper STT ──► command   │
└─────────────────────────────────────────────────────────┘
```

| Component | Role |
|-----------|------|
| [Piper](https://github.com/rhasspy/piper) | Fast, local neural TTS with 30+ language voices |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Efficient Whisper STT (CTranslate2 backend) |
| [Ollama](https://ollama.com) | Local LLM inference for Friendly Mode summaries |

---

## Roadmap

- [x] TTS output for any CLI command (`--full`)
- [x] LLM summarization before speaking (`--friendly`)
- [x] **Voice command input** (`voxshell interact`)
- [ ] Silence-detection for listen (auto-stop instead of fixed duration)
- [ ] Custom agent personas / system prompts
- [ ] Shell extension (`.zshrc` / `.bashrc` alias helpers)
- [ ] Multi-language support (30+ Piper voices, Whisper multilingual)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run the test suite with:

```bash
pip install pytest
pytest tests/ -v
```

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
Made by <a href="https://github.com/gencersarp">gencersarp</a>
</div>
