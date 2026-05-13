"""Entry-point picker. Maps the 7 modes to initial supervisor state + skip rules."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from frame.schemas.state import EntryMode, FrameState, Phase

console = Console()

ENTRY_LABELS: dict[int, tuple[EntryMode, str]] = {
    1: (EntryMode.IDEA_ONLY, "Just an idea"),
    2: (EntryMode.IDEA_PLUS_EVIDENCE, "An idea + raw evidence"),
    3: (EntryMode.EVIDENCE_ONLY, "Raw evidence (research, reviews, etc.)"),
    4: (EntryMode.LOCKED_PROBLEM, "A locked problem statement"),
    5: (EntryMode.LOCKED_PROBLEM_AND_SOLUTION, "A locked problem + solution"),
    6: (EntryMode.DRAFT_PRD, "A draft PRD (Critic only)"),
    7: (EntryMode.RESUME_FROM_VAULT, "An existing Frame package from vault"),
}

# Where each entry mode begins in the pipeline.
ENTRY_START_PHASE: dict[EntryMode, Phase] = {
    EntryMode.IDEA_ONLY: Phase.EXPLORING,
    EntryMode.IDEA_PLUS_EVIDENCE: Phase.EXPLORING,
    EntryMode.EVIDENCE_ONLY: Phase.SYNTHESIZING,
    EntryMode.LOCKED_PROBLEM: Phase.IDEATING,
    EntryMode.LOCKED_PROBLEM_AND_SOLUTION: Phase.DEFINING,
    EntryMode.DRAFT_PRD: Phase.CRITIQUING,
    EntryMode.RESUME_FROM_VAULT: Phase.INIT,  # determined by vault contents
}


def prompt_entry_mode() -> EntryMode:
    """Render the entry-point picker and return the chosen mode."""

    lines = [f"[{n}] {label}" for n, (_, label) in ENTRY_LABELS.items()]
    console.print(Panel("\n".join(lines), title="What do you have?", border_style="cyan"))
    choice = IntPrompt.ask("Pick", choices=[str(i) for i in ENTRY_LABELS], default=1)
    return ENTRY_LABELS[choice][0]


def initial_state(mode: EntryMode) -> FrameState:
    return FrameState(entry_mode=mode, phase=ENTRY_START_PHASE[mode])
