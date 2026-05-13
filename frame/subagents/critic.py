"""Critic sub-agent — final pass.

Phase 1 stub: returns an empty Critique.
"""

from __future__ import annotations

from frame.schemas.critique import Critique
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


async def run(state: FrameState) -> Critique:
    _ = await run_subagent(
        name="critic",
        user_message="Critique the package for scope drift, metric quality, assumptions.",
    )
    return Critique(
        findings=[],
        overall_assessment="",
        ready_to_ship=False,
    )
