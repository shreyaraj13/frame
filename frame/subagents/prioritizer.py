"""Prioritizer sub-agent — solution-space convergence.

Phase 1 stub: returns an empty PrioritizationResult.
"""

from __future__ import annotations

from frame.schemas.solution import PrioritizationResult
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


async def run(state: FrameState) -> PrioritizationResult:
    _ = await run_subagent(
        name="prioritizer",
        user_message="Score solutions, recommend one, justify cuts.",
    )
    return PrioritizationResult(
        recommended_id="",
        recommendation_rationale="",
    )
