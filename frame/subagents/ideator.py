"""Ideator sub-agent — solution-space divergence.

Phase 1 stub: returns an empty SolutionOptions.
"""

from __future__ import annotations

from frame.schemas.solution import SolutionOptions
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


async def run(state: FrameState) -> SolutionOptions:
    _ = await run_subagent(
        name="ideator",
        user_message="Generate 6-10 solutions across mechanism axes.",
    )
    return SolutionOptions(solutions=[])
