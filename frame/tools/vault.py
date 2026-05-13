"""Obsidian vault writer — Phase 1 stub.

Phase 2 routes through the obsidian-mcp server. For now, print-only —
no directory is created, no files written.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.console import Console

from frame.config import get_settings
from frame.schemas.state import FrameState

console = Console()


def package_dir(state: FrameState) -> Path:
    """Compute where the package would live, e.g.
    <vault>/Frame Packages/2026-05-13 <idea>/. Does not create the directory.
    """
    settings = get_settings()
    today = date.today().isoformat()
    idea_slug = (state.seed_idea or state.run_id)[:60].strip().replace("/", "-")
    return settings.obsidian_vault_path / "Frame Packages" / f"{today} {idea_slug}"


def write_package(state: FrameState) -> Path:
    """STUB — prints what would be written. No filesystem side effects."""
    target = package_dir(state)
    console.print(f"[dim]\\[vault-stub][/dim] would write package to: [cyan]{target}[/cyan]")
    files = [
        "README.md",
        "research.md",
        "problem-statement.md",
        "solutions-considered.md",
        "decision-log.md",
        "prd.md",
        "metrics.md",
        "trace.json",
    ]
    for f in files:
        console.print(f"[dim]\\[vault-stub][/dim]   would write {f}")
    return target
