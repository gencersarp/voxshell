# 🎙️ VoxShell

**The Ultimate Voice Wrapper for any CLI tool.**  
*Transform your terminal into a local, intelligent voice agent.*

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Local AI](https://img.shields.io/badge/AI-100%25_Local-brightgreen.svg)]()

**VoxShell** is a plug-and-play CLI wrapper that adds local **Text-to-Speech (TTS)** and **Speech-to-Text (STT)** capabilities to any command-line tool. It captures output in real-time and speaks it back to you, with an optional "Friendly Mode" that uses local LLMs to synthesize verbose logs into concise summaries.

## ✨ Features

- **🚀 Plug-and-Play**: No complex setup. Just prefix any command: `voxshell "ls -la"`.
- **👂 100% Local**: Powered by **Piper** (TTS) and **Whisper** (STT). No cloud APIs, no latency, no data leakage.
- **🧠 Friendly Mode**: Automatically summarizes long outputs (help menus, log files, directories) into natural speech using **Ollama**.
- **🔌 Any CLI**: Works with `git`, `docker`, `kubectl`, `grep`, or even your own custom scripts.
- **📦 Auto-Managed**: Automatically downloads and manages high-quality voice models and weights.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/gencersarp/voxshell.git
cd voxshell
pip install -r requirements.txt
pip install -e .
```

### 2. Intelligent Summarization (Friendly Mode)
Get a digestible summary of a long output:
```bash
voxshell "ls -la /usr/local/bin" --friendly
```

### 3. Full Output Reading
Listen to the entire output as it streams:
```bash
voxshell "echo 'System update complete. No errors found.'" --full
```

---

## 🧠 The Intelligence Layer

VoxShell integrates with **Ollama** to provide smart summarization. If you have Ollama installed and a model pulled (e.g., `llama3`), VoxShell will use it to "read between the lines" of your CLI output.

```bash
# Optional: Setup Ollama for best results
ollama pull llama3
```

---

## 🛠️ Configuration

| Flag | Description | Default |
|------|-------------|---------|
| `--full` | Reads the entire stdout back to you. | `False` |
| `--friendly` | Uses an LLM to summarize the output before speaking. | `False` |
| `--voice` | The Piper voice model to use. | `en_US-lessac-medium` |
| `--llm` | The Ollama model for summarization. | `llama3` |

---

## 🗺️ Roadmap

- [ ] **Voice Commands**: Speak directly to the terminal and have them executed.
- [ ] **Custom Personalities**: Choose different "agent" personas for your CLI.
- [ ] **Shell Extension**: Direct integration into `.zshrc` or `.bashrc`.
- [ ] **Multi-Language**: Support for 30+ languages via Piper and Whisper.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
Created with ❤️ by [gencersarp](https://github.com/gencersarp)
