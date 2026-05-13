"""Frame CLI — Typer entry point."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from frame import __version__
from frame.config import get_settings
from frame.entry_points import initial_state, prompt_entry_mode
from frame.schemas.state import EntryMode, FrameState
from frame.supervisor import run as run_supervisor

app = typer.Typer(
    name="frame",
    help="Multi-agent PM workflow tool. Vague idea → defensible PRD.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


@app.command()
def start(
    state_file: Annotated[
        Path,
        typer.Option("--state-file", help="Where to snapshot run state for resume."),
    ] = Path(".frame_state.json"),
) -> None:
    """Start a new Frame run. Prompts for entry mode."""

    mode = prompt_entry_mode()
    state = initial_state(mode)
    asyncio.run(run_supervisor(state, state_path=state_file))


@app.command()
def resume(
    state_file: Annotated[
        Path,
        typer.Argument(help="Path to a previously written .frame_state.json snapshot."),
    ] = Path(".frame_state.json"),
) -> None:
    """Resume a run from a state snapshot."""

    if not state_file.exists():
        console.print(f"[red]no state file at {state_file}[/red]")
        raise typer.Exit(code=1)
    state = FrameState.load(state_file)
    asyncio.run(run_supervisor(state, state_path=state_file))


@app.command()
def critique(
    prd_file: Annotated[Path, typer.Argument(help="Markdown PRD to critique.")],
) -> None:
    """Entry point 6: run only the Critic over an existing PRD."""

    if not prd_file.exists():
        console.print(f"[red]no prd at {prd_file}[/red]")
        raise typer.Exit(code=1)
    state = initial_state(EntryMode.DRAFT_PRD)
    # Phase 2 will read the file into state.package; for now just print intent.
    console.print(f"[yellow]would critique {prd_file} (stub)[/yellow]")
    asyncio.run(run_supervisor(state))


@app.command()
def doctor() -> None:
    """Print resolved config + dependency check. Useful when onboarding."""

    s = get_settings()
    console.print(f"version: {__version__}")
    console.print(f"model: {s.model}")
    console.print(f"vault: {s.obsidian_vault_path}  exists={s.obsidian_vault_path.exists()}")
    console.print(f"anthropic key set: {bool(s.anthropic_api_key)}")
    console.print(f"langfuse enabled: {s.langfuse_enabled}")
    console.print(f"tavily key set: {bool(s.tavily_api_key)}")


@app.command()
def version() -> None:
    """Print Frame version."""
    console.print(__version__)


if __name__ == "__main__":
    app()
