import click
import os
import sys
import threading
from .core import CommandRunner
from .audio import VoiceEngine
from .models import ModelManager
from .summary import Summarizer

@click.command()
@click.argument('command_str', required=True)
@click.option('--full', is_flag=True, help="Read the entire output.")
@click.option('--friendly', is_flag=True, help="Read a concise summary (Friendly Mode).")
@click.option('--voice', default="en_US-lessac-medium", help="Piper voice model name.")
@click.option('--llm', default="llama3", help="Ollama model name for Friendly Mode.")
def main(command_str, full, friendly, voice, llm):
    """
    mlmodelselect: A voice agent wrapper for any CLI command.
    """
    # 1. Initialize Managers
    model_manager = ModelManager()
    voice_engine = VoiceEngine(model_manager)
    summarizer = Summarizer(model_name=llm)

    # 2. Setup TTS (Load in background while command starts)
    def init_voice():
        voice_engine.initialize_tts(voice_name=voice)
    
    voice_thread = threading.Thread(target=init_voice)
    voice_thread.start()

    # 3. Handle Voice Input (STT) - Future Implementation
    # if command_str == "listen":
    #     command_str = voice_engine.listen()

    # 4. Define Output Callback
    text_buffer = []
    
    def on_text(text):
        if full and not friendly:
            voice_engine.speak(text)
        text_buffer.append(text)

    # 5. Run the Command
    click.echo(f"Executing: {command_str}")
    runner = CommandRunner(command_str, on_text_callback=on_text)
    return_code, full_output = runner.run()

    # 6. Handle Friendly Mode (Summarization)
    if friendly:
        # Wait for voice engine to be ready if it's still loading
        voice_thread.join()
        
        click.echo("\nSummarizing for voice agent...")
        summary = summarizer.summarize(full_output)
        click.secho(f"Voice Summary: {summary}", fg="cyan")
        voice_engine.speak(summary)

    # Final cleanup (optional wait for audio to finish)
    if full or friendly:
        import time
        while voice_engine.player.queue.qsize() > 0 or voice_engine.player.is_playing:
            time.sleep(0.5)

    sys.exit(return_code)

if __name__ == "__main__":
    main()
