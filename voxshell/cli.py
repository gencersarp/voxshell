import json
import os
import sys
from typing import Optional

import click

from .audio import VoiceEngine
from .config import ConfigManager
from .core import CommandRunner
from .models import ModelManager
from .summary import Summarizer


@click.group(invoke_without_command=True)
@click.argument("command_str", required=False)
@click.option("--full", is_flag=True, help="Read the entire output aloud.")
@click.option("--friendly", is_flag=True, help="Summarize output before speaking (Friendly Mode).")
@click.option("--voice", help="Piper voice model name.")
@click.option("--llm", help="Ollama model name for Friendly Mode.")
@click.pass_context
def main(
    ctx,
    command_str: Optional[str],
    full: bool,
    friendly: bool,
    voice: Optional[str],
    llm: Optional[str],
):
    """VoxShell: Turn any CLI tool into a voice-enabled agent."""
    config_manager = ConfigManager()

    voice = voice or config_manager.get("voice")
    llm = llm or config_manager.get("llm_model")
    friendly = friendly or (config_manager.get("friendly_mode") if not full else False)

    if not command_str:
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())
        return

    model_manager = ModelManager()
    voice_engine = VoiceEngine(model_manager)
    summarizer = Summarizer(model_name=llm)

    # Load TTS synchronously so it is ready before the first output line arrives.
    voice_engine.initialize_tts(voice_name=voice)

    text_buffer = []

    def on_text(text: str):
        if full and not friendly:
            voice_engine.speak(text)
        text_buffer.append(text)

    click.secho(f"🚀 Executing: {command_str}", fg="green", bold=True)
    runner = CommandRunner(command_str, on_text_callback=on_text)
    return_code, full_output = runner.run()

    if friendly:
        click.echo("\n🧠 Summarizing for voice agent...")
        summary = summarizer.summarize(full_output)
        click.secho(f"🎤 Voice Summary: {summary}", fg="cyan", bold=True)
        voice_engine.speak(summary)

    if (full or friendly) and voice_engine.player:
        voice_engine.player.wait_until_done()

    sys.exit(return_code)


@main.command()
@click.option("--voice", help="Default voice model.")
@click.option("--llm", help="Default LLM model.")
def config(voice, llm):
    """View or update VoxShell configuration."""
    cm = ConfigManager()
    updates = {}
    if voice:
        updates["voice"] = voice
    if llm:
        updates["llm_model"] = llm

    if updates:
        cm.save_config(updates)
        click.secho("✅ Config updated!", fg="green")
    else:
        click.echo("Current config:")
        click.echo(json.dumps(cm.config, indent=2))


@main.command()
@click.option("--duration", default=5, show_default=True, help="Seconds to listen per turn.")
@click.option("--friendly", is_flag=True, help="Summarize responses before speaking.")
@click.option(
    "--stt-model",
    default="base",
    show_default=True,
    help="Whisper model size: tiny | base | small | medium.",
)
@click.option("--voice", help="Piper voice model name.")
@click.option("--llm", default="llama3", show_default=True, help="Ollama model for Friendly Mode.")
def interact(duration: int, friendly: bool, stt_model: str, voice: Optional[str], llm: str):
    """Interactive voice loop: speak a shell command, hear the result, repeat.

    Say 'exit' or 'quit' to stop the loop.
    """
    config_manager = ConfigManager()
    voice = voice or config_manager.get("voice")

    model_manager = ModelManager()
    voice_engine = VoiceEngine(model_manager)
    summarizer = Summarizer(model_name=llm)

    click.secho("Initializing voice engine...", fg="yellow")
    voice_engine.initialize_tts(voice_name=voice)
    voice_engine.initialize_stt(stt_model)

    click.secho(
        "🎙️  VoxShell interactive mode. Say a shell command, or 'exit' to quit.",
        fg="green",
        bold=True,
    )
    voice_engine.speak("VoxShell interactive mode ready. Speak a command.")
    voice_engine.player.wait_until_done()

    while True:
        try:
            spoken = voice_engine.listen(duration=duration, stt_model=stt_model)

            if not spoken:
                click.secho("  (nothing heard, try again)", fg="yellow")
                continue

            click.secho(f"\n🗣️  Heard: {spoken}", fg="cyan")

            if spoken.lower().strip() in ("exit", "quit", "stop"):
                voice_engine.speak("Goodbye.")
                voice_engine.player.wait_until_done()
                break

            click.secho(f"🚀 Running: {spoken}", fg="green", bold=True)
            runner = CommandRunner(spoken)
            return_code, full_output = runner.run()

            if friendly:
                summary = summarizer.summarize(full_output)
                click.secho(f"🎤 {summary}", fg="cyan")
                voice_engine.speak(summary)
            else:
                # Speak up to ~500 chars to avoid very long TTS for huge outputs.
                reply = full_output[:500] if len(full_output) > 500 else full_output
                voice_engine.speak(reply or "Command produced no output.")

            voice_engine.player.wait_until_done()

        except KeyboardInterrupt:
            click.secho("\n👋 Exiting.", fg="yellow")
            break
