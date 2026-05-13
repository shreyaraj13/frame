"""Problem space schemas — Synthesizer output and locked statement."""

from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProblemStatement(BaseModel):
    """One candidate problem statement."""

    id: str = Field(default_factory=lambda: f"prob_{uuid4().hex[:8]}")
    statement: str
    """Single-sentence problem statement. Who, what, when, why-it-matters."""
    who: str
    when: str
    pain: str
    severity: Severity
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    signal_count: int = 0
    tradeoffs: str | None = None
    """What this framing privileges and what it leaves out."""


class ProblemCandidates(BaseModel):
    """Synthesizer output. Always 3 candidates with a recommendation."""

    candidates: list[ProblemStatement]
    recommended_id: str
    recommendation_rationale: str
