"""Critic output schema."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    INFO = "info"


class CritiqueCategory(str, Enum):
    SCOPE_DRIFT = "scope_drift"
    METRIC_QUALITY = "metric_quality"
    HIDDEN_ASSUMPTION = "hidden_assumption"
    INTERNAL_INCONSISTENCY = "internal_inconsistency"
    EVIDENCE_GAP = "evidence_gap"
    OTHER = "other"


class CritiqueFinding(BaseModel):
    category: CritiqueCategory
    severity: Severity
    finding: str
    location: str | None = None
    """Which section of the PRD this points to."""
    suggested_fix: str | None = None


class Critique(BaseModel):
    findings: list[CritiqueFinding] = Field(default_factory=list)
    overall_assessment: str
    ready_to_ship: bool
