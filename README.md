# mlmodelselect: The Voice Agent CLI Wrapper

Turn any command-line tool into a voice agent with `mlmodelselect`. This tool wraps your existing CLI commands, captures their output, and provides local Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities.

## Features

- **Plug-and-Play**: Just wrap any command: `mlmodelselect "ls -la"`.
- **Local TTS**: High-quality voice output using Piper (no cloud API needed).
- **Friendly Mode**: Automatically summarizes verbose outputs into natural-sounding voice snippets.
- **Model Selection**: Easily switch between different local voices and LLM models.
- **Privacy First**: Everything runs locally on your machine.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/mlmodelselect.git
    cd mlmodelselect
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    pip install .
    ```

3.  **Optional (for Friendly Mode)**:
    Install [Ollama](https://ollama.ai/) and pull a model:
    ```bash
    ollama pull llama3
    ```

## Usage

### 1. Basic Output Reading
Hear the entire output of a command:
```bash
mlmodelselect "echo 'Hello from my CLI!'" --full
```

### 2. Friendly Mode (Summarization)
Get a digestible voice summary of long outputs:
```bash
mlmodelselect "ls -la /usr/local/bin" --friendly
```

### 3. Custom Voice
Specify a different Piper voice:
```bash
mlmodelselect "date" --full --voice en_US-lessac-low
```

## How it Works

- **TTS**: Uses `piper-tts` with `.onnx` models downloaded automatically to the `models/` directory.
- **Friendly Mode**: Leverages local LLMs via `ollama` (defaulting to `llama3`) to synthesize verbose text into conversational summaries.
- **STT**: Uses `faster-whisper` for future voice command support.

## License

MIT
