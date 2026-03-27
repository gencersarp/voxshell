import click
import os
import sys
import threading
from typing import Optional
from .core import CommandRunner
from .audio import VoiceEngine
from .models import ModelManager
from .summary import Summarizer
from .config import ConfigManager

@click.group(invoke_without_command=True)
@click.argument('command_str', required=False)
@click.option('--full', is_flag=True, help="Read the entire output.")
@click.option('--friendly', is_flag=True, help="Read a concise summary (Friendly Mode).")
@click.option('--voice', help="Piper voice model name.")
@click.option('--llm', help="Ollama model name for Friendly Mode.")
@click.pass_context
def main(ctx, command_str: Optional[str], full: bool, friendly: bool, voice: Optional[str], llm: Optional[str]):
    """
    VoxShell: Turn any CLI tool into a voice-enabled agent.
    """
    config_manager = ConfigManager()
    
    # Use config if not provided in CLI
    voice = voice or config_manager.get("voice")
    llm = llm or config_manager.get("llm_model")
    friendly = friendly or (config_manager.get("friendly_mode") if not full else False)

    if not command_str:
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())
        return

    # 1. Initialize Managers
    model_manager = ModelManager()
    voice_engine = VoiceEngine(model_manager)
    summarizer = Summarizer(model_name=llm)

    # 2. Setup TTS (Load in background)
    def init_voice():
        voice_engine.initialize_tts(voice_name=voice)
    
    voice_thread = threading.Thread(target=init_voice)
    voice_thread.start()

    # 3. Output Callback
    text_buffer = []
    
    def on_text(text: str):
        if full and not friendly:
            voice_engine.speak(text)
        text_buffer.append(text)

    # 4. Run the Command
    click.secho(f"🚀 Executing: {command_str}", fg="green", bold=True)
    runner = CommandRunner(command_str, on_text_callback=on_text)
    return_code, full_output = runner.run()

    # 5. Handle Friendly Mode
    if friendly:
        voice_thread.join()
        click.echo("\n🧠 Summarizing for voice agent...")
        summary = summarizer.summarize(full_output)
        click.secho(f"🎤 Voice Summary: {summary}", fg="cyan", bold=True)
        voice_engine.speak(summary)

    # Cleanup
    if (full or friendly) and voice_engine.player:
        import time
        while voice_engine.player.queue.qsize() > 0 or voice_engine.player.is_playing:
            time.sleep(0.5)

    sys.exit(return_code)

@main.command()
@click.option('--voice', help="Default voice model.")
@click.option('--llm', help="Default LLM model.")
def config(voice, llm):
    """Update VoxShell configuration."""
    cm = ConfigManager()
    updates = {}
    if voice: updates["voice"] = voice
    if llm: updates["llm_model"] = llm
    
    if updates:
        cm.save_config(updates)
        click.secho("✅ Config updated!", fg="green")
    else:
        click.echo("Current Config:")
        click.echo(json.dumps(cm.config, indent=2))
