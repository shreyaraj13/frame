"""Supervisor orchestration loop.

Phase 1: stub orchestration. Walks the phase sequence implied by the
entry mode, calls each sub-agent stub, calls each gate stub, and stores
empty Pydantic returns in state. NO Anthropic SDK calls anywhere.

Phase 2 replaces this with a real anthropic.messages.create loop where
the supervisor calls sub-agents and gates as tools.
"""

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable

from rich.console import Console
from rich.panel import Panel

from frame.config import get_settings
from frame.schemas.state import EntryMode, FrameState, Phase
from frame.subagents import (
    critic,
    definer,
    explorer,
    ideator,
    prioritizer,
    synthesizer,
)
from frame.tools.gates import GateChoice, continuation_prompt, present_gate_to_user
from frame.tools.vault import write_package

console = Console()


# Which phases run for each entry mode.
PHASE_SEQUENCE: dict[EntryMode, list[Phase]] = {
    EntryMode.IDEA_ONLY: [
        Phase.EXPLORING,
        Phase.SYNTHESIZING,
        Phase.GATE_1,
        Phase.IDEATING,
        Phase.PRIORITIZING,
        Phase.GATE_2,
        Phase.DEFINING,
        Phase.CRITIQUING,
    ],
    EntryMode.IDEA_PLUS_EVIDENCE: [
        Phase.EXPLORING,
        Phase.SYNTHESIZING,
        Phase.GATE_1,
        Phase.IDEATING,
        Phase.PRIORITIZING,
        Phase.GATE_2,
        Phase.DEFINING,
        Phase.CRITIQUING,
    ],
    EntryMode.EVIDENCE_ONLY: [
        Phase.SYNTHESIZING,
        Phase.GATE_1,
        Phase.IDEATING,
        Phase.PRIORITIZING,
        Phase.GATE_2,
        Phase.DEFINING,
        Phase.CRITIQUING,
    ],
    EntryMode.LOCKED_PROBLEM: [
        Phase.IDEATING,
        Phase.PRIORITIZING,
        Phase.GATE_2,
        Phase.DEFINING,
        Phase.CRITIQUING,
    ],
    EntryMode.LOCKED_PROBLEM_AND_SOLUTION: [
        Phase.DEFINING,
        Phase.CRITIQUING,
    ],
    EntryMode.DRAFT_PRD: [
        Phase.CRITIQUING,
    ],
    EntryMode.RESUME_FROM_VAULT: [],  # determined by vault contents in Phase 2
}


def _banner(state: FrameState) -> None:
    settings = get_settings()
    console.print(
        Panel(
            f"[bold]Frame[/bold] (Phase 1 stub — no LLM calls)\n"
            f"model: {settings.model}\n"
            f"vault: {settings.obsidian_vault_path}\n"
            f"run_id: {state.run_id}\n"
            f"entry_mode: {state.entry_mode.value}",
            title="supervisor",
            border_style="magenta",
        )
    )


async def _phase_explore(state: FrameState) -> None:
    console.print("[yellow]→ Explorer[/yellow] (stub)")
    state.exploration = await explorer.run(state, evidence=state.evidence)


async def _phase_synthesize(state: FrameState) -> None:
    console.print("[yellow]→ Synthesizer[/yellow] (stub)")
    state.problem_candidates = await synthesizer.run(state)


def _phase_gate_1(state: FrameState) -> None:
    console.print("[yellow]→ GATE 1[/yellow] (stub: hardcoded PICK 0)")
    decision = present_gate_to_user(
        title="GATE 1: Lock a problem statement",
        choices=[GateChoice(label="(stub) candidate 1")],
        recommendation_index=0,
    )
    state.decision_log.append(f"gate_1: {decision.action.value} idx={decision.picked_index}")


async def _phase_ideate(state: FrameState) -> None:
    console.print("[yellow]→ Ideator[/yellow] (stub)")
    state.solution_options = await ideator.run(state)


async def _phase_prioritize(state: FrameState) -> None:
    console.print("[yellow]→ Prioritizer[/yellow] (stub)")
    state.prioritization = await prioritizer.run(state)


def _phase_gate_2(state: FrameState) -> None:
    console.print("[yellow]→ GATE 2[/yellow] (stub: hardcoded PICK 0)")
    decision = present_gate_to_user(
        title="GATE 2: Lock a solution",
        choices=[GateChoice(label="(stub) solution 1")],
        recommendation_index=0,
    )
    state.decision_log.append(f"gate_2: {decision.action.value} idx={decision.picked_index}")


async def _phase_define(state: FrameState) -> None:
    console.print("[yellow]→ Definer[/yellow] (stub)")
    state.package = await definer.run(state)


async def _phase_critique(state: FrameState) -> None:
    console.print("[yellow]→ Critic[/yellow] (stub)")
    state.critique = await critic.run(state)


PHASE_HANDLERS: dict[Phase, Callable[[FrameState], Awaitable[None] | None]] = {
    Phase.EXPLORING: _phase_explore,
    Phase.SYNTHESIZING: _phase_synthesize,
    Phase.GATE_1: _phase_gate_1,
    Phase.IDEATING: _phase_ideate,
    Phase.PRIORITIZING: _phase_prioritize,
    Phase.GATE_2: _phase_gate_2,
    Phase.DEFINING: _phase_define,
    Phase.CRITIQUING: _phase_critique,
}


async def run(state: FrameState, state_path: Path | None = None) -> FrameState:
    """Walk the phase sequence for the chosen entry mode. Stubs all the way down."""

    _banner(state)
    sequence = PHASE_SEQUENCE.get(state.entry_mode, [])

    if not sequence:
        console.print(f"[dim]no phase sequence for {state.entry_mode.value} (stub)[/dim]")

    for phase in sequence:
        state.phase = phase
        handler = PHASE_HANDLERS[phase]
        result = handler(state)
        if result is not None:
            await result
        # After each non-gate phase, ask whether to continue.
        if phase not in (Phase.GATE_1, Phase.GATE_2):
            continuation_prompt(next_phase_label=phase.value)

    state.phase = Phase.DONE
    write_package(state)
    console.print("[green]✓ supervisor stub complete[/green]")

    if state_path is not None:
        state.snapshot(state_path)

    return state
