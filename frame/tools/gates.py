"""HITL gates — Phase 1 stub.

Phase 2 will render Rich prompts and block on user input. For now,
present_gate_to_user() prints what it would show and returns a hardcoded
PICK of the first option so the supervisor can run end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rich.console import Console

console = Console()


class GateAction(str, Enum):
    PICK = "pick"
    EDIT = "edit"
    REJECT_ALL = "reject_all"
    ADD_EVIDENCE = "add_evidence"


@dataclass
class GateChoice:
    label: str
    detail: str | None = None


@dataclass
class GateDecision:
    action: GateAction
    picked_index: int | None = None
    edited_text: str | None = None


def present_gate_to_user(
    *,
    title: str,
    choices: list[GateChoice],
    recommendation_index: int | None = None,
    allow_edit: bool = True,
    allow_add_evidence: bool = True,
) -> GateDecision:
    """STUB — prints what would be shown, returns hardcoded PICK(0)."""
    console.print(f"[dim]\\[gate-stub][/dim] would block on: [cyan]{title}[/cyan]")
    console.print(f"[dim]\\[gate-stub][/dim] choices: {len(choices)}  rec={recommendation_index}")
    return GateDecision(action=GateAction.PICK, picked_index=0)


def continuation_prompt(next_phase_label: str) -> str:
    """STUB — always returns 'continue' so the supervisor walks all phases."""
    console.print(f"[dim]\\[gate-stub][/dim] would ask: continue to {next_phase_label}? -> yes")
    return "continue"
