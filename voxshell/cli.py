import json
import sys
from typing import Optional

import click

from .audio import VoiceEngine
from .config import ConfigManager
from .core import CommandRunner
from .models import ModelManager
from .summary import Summarizer

_BANNER = """\
\033[36m
 _   _           ___ _        _ _
| | | |_____ __ / __| |_  ___| | |
| |_| / _ \ \ / \__ \ ' \/ -_) | |
 \___/\___/_\_\ |___/_||_\___|_|_|
\033[0m"""

_DIVIDER = click.style("─" * 48, fg="bright_black")


def _print_banner():
    click.echo(_BANNER)


# ---------------------------------------------------------------------------
# Main command
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True,
             context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
@click.option("--full", is_flag=True, help="Read the entire output aloud.")
@click.option("--friendly", is_flag=True, help="Summarize output then speak (Friendly Mode).")
@click.option("--voice", help="Piper voice model name.")
@click.option("--llm", help="Ollama model name for Friendly Mode.")
@click.option("--version", "show_version", is_flag=True, is_eager=True, expose_value=False,
              callback=lambda ctx, _, v: (click.echo(f"voxshell {_get_version()}"), ctx.exit()) if v else None,
              help="Show version and exit.")
@click.pass_context
def main(
    ctx,
    full: bool,
    friendly: bool,
    voice: Optional[str],
    llm: Optional[str],
):
    """VoxShell — voice wrapper for any CLI tool.

    \b
    Examples:
      voxshell "git log --oneline -5" --full
      voxshell "ls -la" --friendly
      voxshell interact
    """
    # ctx.args holds any positional tokens that weren't consumed as options.
    # When a subcommand is matched (e.g. `voxshell config`), Click routes there
    # before this callback runs, so ctx.args is empty in that case.
    command_str: Optional[str] = " ".join(ctx.args) if ctx.args else None

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

    click.echo(_DIVIDER)
    click.secho(f"  🚀  {command_str}", fg="green", bold=True)
    click.echo(_DIVIDER)

    voice_engine.initialize_tts(voice_name=voice)

    text_buffer = []

    def on_text(text: str):
        if full and not friendly:
            voice_engine.speak(text)
        text_buffer.append(text)

    runner = CommandRunner(command_str, on_text_callback=on_text)
    return_code, full_output = runner.run()

    if friendly:
        click.echo()
        click.secho("  🧠  Summarizing…", fg="yellow")
        summary = summarizer.summarize(full_output)
        click.echo(_DIVIDER)
        click.secho(f"  🎤  {summary}", fg="cyan", bold=True)
        click.echo(_DIVIDER)
        voice_engine.speak(summary)

    if (full or friendly) and voice_engine.player:
        voice_engine.player.wait_until_done()

    sys.exit(return_code)


# ---------------------------------------------------------------------------
# config sub-command
# ---------------------------------------------------------------------------

@main.command()
@click.option("--voice", help="Default Piper voice model.")
@click.option("--llm", help="Default Ollama model.")
def config(voice, llm):
    """View or update persistent VoxShell configuration."""
    cm = ConfigManager()
    updates = {}
    if voice:
        updates["voice"] = voice
    if llm:
        updates["llm_model"] = llm

    if updates:
        cm.save_config(updates)
        click.secho("  ✅  Config updated.", fg="green")
    else:
        click.echo(_DIVIDER)
        click.secho("  ⚙️   Current configuration", bold=True)
        click.echo(_DIVIDER)
        for k, v in cm.config.items():
            click.echo(f"  {click.style(k, fg='cyan')}: {v}")
        click.echo(_DIVIDER)


# ---------------------------------------------------------------------------
# interact sub-command
# ---------------------------------------------------------------------------

@main.command()
@click.option("--duration", default=5, show_default=True,
              help="Seconds to record per turn.")
@click.option("--friendly", is_flag=True,
              help="Summarize responses before speaking.")
@click.option("--stt-model", default="base", show_default=True,
              help="Whisper model size: tiny | base | small | medium.")
@click.option("--voice", help="Piper voice model name.")
@click.option("--llm", default="llama3", show_default=True,
              help="Ollama model for Friendly Mode.")
def interact(duration: int, friendly: bool, stt_model: str, voice: Optional[str], llm: str):
    """Interactive voice loop — speak a command, hear the result, repeat.

    Say \033[1m"exit"\033[0m or \033[1m"quit"\033[0m to stop.
    """
    config_manager = ConfigManager()
    voice = voice or config_manager.get("voice")

    _print_banner()

    model_manager = ModelManager()
    voice_engine = VoiceEngine(model_manager)
    summarizer = Summarizer(model_name=llm)

    click.secho("  Initializing TTS…", fg="bright_black")
    voice_engine.initialize_tts(voice_name=voice)
    click.secho("  Initializing STT…", fg="bright_black")
    voice_engine.initialize_stt(stt_model)

    click.echo(_DIVIDER)
    click.secho("  🎙️   Interactive mode ready", fg="green", bold=True)
    click.secho(f"  Voice: {voice}  |  STT: {stt_model}  |  Listen: {duration}s", fg="bright_black")
    click.secho('  Say "exit" or "quit" to stop.', fg="bright_black")
    click.echo(_DIVIDER)

    voice_engine.speak("VoxShell interactive mode ready. Speak a command.")
    voice_engine.player.wait_until_done()

    turn = 0
    while True:
        try:
            turn += 1
            click.echo()
            click.secho(f"  [{turn}] Listening for {duration}s…", fg="yellow")

            spoken = voice_engine.listen(duration=duration, stt_model=stt_model)

            if not spoken:
                click.secho("      (nothing heard — try again)", fg="bright_black")
                continue

            click.secho(f"  🗣️  {spoken}", fg="cyan")

            if spoken.lower().strip() in ("exit", "quit", "stop"):
                click.echo(_DIVIDER)
                click.secho("  👋  Goodbye.", fg="green", bold=True)
                click.echo(_DIVIDER)
                voice_engine.speak("Goodbye.")
                voice_engine.player.wait_until_done()
                break

            click.echo(_DIVIDER)
            click.secho(f"  🚀  {spoken}", fg="green", bold=True)
            click.echo(_DIVIDER)

            runner = CommandRunner(spoken)
            return_code, full_output = runner.run()

            if return_code != 0:
                click.secho(f"  ⚠️   Exit code {return_code}", fg="red")

            if friendly:
                click.secho("  🧠  Summarizing…", fg="yellow")
                summary = summarizer.summarize(full_output)
                click.echo(_DIVIDER)
                click.secho(f"  🎤  {summary}", fg="cyan", bold=True)
                voice_engine.speak(summary)
            else:
                reply = full_output[:500] if len(full_output) > 500 else full_output
                voice_engine.speak(reply or "Command produced no output.")

            voice_engine.player.wait_until_done()

        except KeyboardInterrupt:
            click.echo()
            click.echo(_DIVIDER)
            click.secho("  👋  Interrupted.", fg="yellow")
            click.echo(_DIVIDER)
            break


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_version() -> str:
    try:
        from . import __version__
        return __version__
    except Exception:
        return "unknown"
