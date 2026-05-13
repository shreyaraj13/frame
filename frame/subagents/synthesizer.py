"""Synthesizer sub-agent — problem-space convergence.

Phase 1 stub: returns an empty ProblemCandidates.
"""

from __future__ import annotations

from frame.schemas.problem import ProblemCandidates
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


async def run(state: FrameState) -> ProblemCandidates:
    _ = await run_subagent(
        name="synthesizer",
        user_message="Cluster findings, draft 3 problem statements, recommend one.",
    )
    return ProblemCandidates(
        candidates=[],
        recommended_id="",
        recommendation_rationale="",
    )
