"""Explorer output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserSignal(BaseModel):
    quote: str
    """Verbatim or paraphrased — keep close to source."""
    interpretation: str
    evidence_ids: list[str] = Field(default_factory=list)


class Stakeholder(BaseModel):
    name: str
    role: str
    motivation: str
    pain: str | None = None


class AdjacentProblem(BaseModel):
    """A neighboring problem worth surfacing during divergence."""

    statement: str
    why_adjacent: str
    severity_hint: str | None = None


class ExplorationResult(BaseModel):
    """Output of the Explorer sub-agent. Soft targets: 5+ problems, 15+ signals."""

    seed_idea: str
    adjacent_problems: list[AdjacentProblem] = Field(default_factory=list)
    user_signals: list[UserSignal] = Field(default_factory=list)
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    surfaced_assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    used_evidence: bool = False
    """True if Explorer worked from user-supplied evidence vs. only synthesis."""
