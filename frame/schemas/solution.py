"""Solution space schemas — Ideator + Prioritizer outputs."""

from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class MechanismAxis(str, Enum):
    AI_NATIVE = "ai_native"
    WORKFLOW = "workflow"
    MARKETPLACE = "marketplace"
    TOOL = "tool"
    SERVICE = "service"
    OTHER = "other"


class Solution(BaseModel):
    """A candidate solution direction."""

    id: str = Field(default_factory=lambda: f"sol_{uuid4().hex[:8]}")
    name: str
    mechanism: str
    """How it works in one sentence."""
    mechanism_axis: MechanismAxis
    bet: str
    """The wager — what we believe is true that makes this work."""
    what_must_be_true: list[str] = Field(default_factory=list)
    """Falsifiable conditions for success."""


class RICEScore(BaseModel):
    """RICE = Reach × Impact × Confidence / Effort."""

    solution_id: str
    reach: float
    impact: float
    confidence: float
    effort: float
    score: float
    rationale: str | None = None


class SolutionOptions(BaseModel):
    """Ideator output. Soft target: 6-10 solutions across mechanism axes."""

    solutions: list[Solution]
    coverage_notes: str | None = None
    """Which mechanism axes are present/absent and why."""


class PrioritizationResult(BaseModel):
    """Prioritizer output. Recommends one, justifies all cuts."""

    rice_scores: list[RICEScore] = Field(default_factory=list)
    matrix_2x2: dict[str, list[str]] | None = None
    """Optional alternative framing: quadrant -> solution ids."""
    recommended_id: str
    recommendation_rationale: str
    killed_solutions: list["KilledSolution"] = Field(default_factory=list)


class KilledSolution(BaseModel):
    """A cut solution kept visible in the final PRD."""

    solution: Solution
    reason_killed: str
    revisit_conditions: str | None = None
    """What would have to change for this to be worth revisiting."""


PrioritizationResult.model_rebuild()
