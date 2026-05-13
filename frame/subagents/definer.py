"""Definer sub-agent — writes PRD, metrics, instrumentation plan.

Phase 1 stub: returns a minimal-valid PMPackage with empty fields.
"""

from __future__ import annotations

from frame.schemas.package import PRD, Metric, MetricKind, MetricsPlan, PMPackage
from frame.schemas.problem import ProblemStatement, Severity
from frame.schemas.solution import MechanismAxis, Solution
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


def _empty_problem() -> ProblemStatement:
    return ProblemStatement(
        statement="", who="", when="", pain="", severity=Severity.LOW
    )


def _empty_solution() -> Solution:
    return Solution(
        name="",
        mechanism="",
        mechanism_axis=MechanismAxis.OTHER,
        bet="",
    )


def _empty_metrics() -> MetricsPlan:
    return MetricsPlan(
        north_star=Metric(
            name="",
            kind=MetricKind.LAGGING,
            definition="",
            instrumentation="",
        )
    )


async def run(state: FrameState) -> PMPackage:
    _ = await run_subagent(
        name="definer",
        user_message="Write PRD, metrics, instrumentation from locked problem + solution.",
    )
    return PMPackage(
        idea=state.seed_idea or "",
        prd=PRD(
            title="",
            one_liner="",
            locked_problem=state.locked_problem or _empty_problem(),
            locked_solution=state.locked_solution or _empty_solution(),
        ),
        metrics=_empty_metrics(),
        killed_solutions=state.killed_solutions,
    )
