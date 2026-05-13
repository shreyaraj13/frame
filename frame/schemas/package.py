"""Definer output — PRD + metrics + instrumentation."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from frame.schemas.problem import ProblemStatement
from frame.schemas.solution import KilledSolution, Solution


class MetricKind(str, Enum):
    LEADING = "leading"
    LAGGING = "lagging"
    GUARDRAIL = "guardrail"
    COUNTER = "counter"


class Metric(BaseModel):
    name: str
    kind: MetricKind
    definition: str
    target: str | None = None
    """e.g., '+15% in 30 days'."""
    instrumentation: str
    """How it's measured. Event names, SQL, source-of-truth."""


class MetricsPlan(BaseModel):
    north_star: Metric
    primary: list[Metric] = Field(default_factory=list)
    guardrails: list[Metric] = Field(default_factory=list)


class PRD(BaseModel):
    """Definer output — the PRD itself."""

    title: str
    one_liner: str
    locked_problem: ProblemStatement
    locked_solution: Solution
    user_stories: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class PMPackage(BaseModel):
    """The full Frame output — everything written to the vault."""

    created: date = Field(default_factory=date.today)
    idea: str
    prd: PRD
    metrics: MetricsPlan
    killed_solutions: list[KilledSolution] = Field(default_factory=list)
    decision_log: list[str] = Field(default_factory=list)
    """One-liners per gate decision, with timestamp."""
    trace_id: str | None = None
    """Langfuse trace id for this run."""
