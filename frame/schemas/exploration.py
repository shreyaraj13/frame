"""Frame Explorer: output schema.

Defines the data contract for Explorer's submit_exploration tool call.
All Phase A decisions are encoded here as fields, types, or validators.
"""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ============================================================
# Controlled vocabularies
# ============================================================

SourceType = Literal["review", "forum", "hn", "news", "interview", "blog", "other"]
StakeholderType = Literal[
    "user", "buyer", "gatekeeper", "competitor", "partner",
    "regulator", "influencer", "other",
]
Geography = Literal["india", "global", "us", "uk", "other"]
Confidence = Literal["high", "medium", "low"]
Criticality = Literal["low", "medium", "high"]


# ============================================================
# Sub-models
# ============================================================

class Signal(BaseModel):
    """A specific user signal from a specific source.

    Quote must be verbatim text from the source, not paraphrased.
    """
    id: str = Field(
        description="Short unique id within this exploration, e.g. 's1', 's2'. "
                    "Used by contradictions to reference specific signals."
    )
    quote: str = Field(
        min_length=10,
        description="Verbatim text from the source. Do not paraphrase or summarize. "
                    "If you cannot quote verbatim, do not include this signal."
    )
    source: str = Field(
        description="URL, evidence file reference, or specific source identifier "
                    "such that the quote could be re-verified."
    )
    source_type: SourceType = Field(
        description="Category of source. Must be one of the controlled values."
    )


class AdjacentProblem(BaseModel):
    """A problem in the original idea's neighborhood that Synthesizer should consider."""
    description: str = Field(
        min_length=20,
        description="The problem, phrased as user-felt pain. Not a solution, not a symptom."
    )
    relationship_to_idea: str = Field(
        min_length=10,
        description="1-2 sentences on why Synthesizer needs to know this exists "
                    "in this idea's neighborhood."
    )


class ContextConstraint(BaseModel):
    """A problem that shapes the idea's viability without being directly solvable."""
    description: str = Field(
        min_length=20,
        description="The constraint. Examples: infrastructure gap, regulatory limit, "
                    "cultural attitude, gatekeeper dynamic."
    )
    relationship_to_idea: str = Field(
        min_length=10,
        description="1-2 sentences on how this constraint shapes the idea's viability "
                    "or deployment."
    )


class Stakeholder(BaseModel):
    """A group in the ecosystem who shapes the problem or its solution."""
    name: str = Field(
        description="Short identifier, e.g. 'JEE-aspirant parents in Tier 1 cities'."
    )
    type: StakeholderType = Field(
        description="Role category in the ecosystem."
    )
    relationship_to_problem: str = Field(
        min_length=20,
        description="1-2 sentences naming what this group wants, fears, or controls "
                    "regarding this problem."
    )
    tensions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Optional. 0-3 short descriptions of internal role tensions within "
                    "this stakeholder. Example: 'Parent wants academic results but "
                    "resists pressuring child.'"
    )


class Assumption(BaseModel):
    """An unstated premise in the original idea that could invalidate it if wrong."""
    statement: str = Field(
        min_length=20,
        description="The assumption, specific and testable. Not a generic prerequisite."
    )
    why_consequential: str = Field(
        min_length=20,
        description="1-2 sentences on what changes if this assumption is wrong."
    )
    criticality: Criticality = Field(
        description="How dangerous this assumption is relative to others in this output."
    )
    why_critical: str = Field(
        min_length=10,
        description="1-2 sentences justifying the criticality rank."
    )


class Contradiction(BaseModel):
    """A structural conflict between two or more signals in this output."""
    claim: str = Field(
        description="One side of the conflict, in Explorer's words."
    )
    counter_claim: str = Field(
        description="The opposing side, in Explorer's words."
    )
    signals_for_claim: list[str] = Field(
        min_length=1,
        description="Signal ids that support the claim."
    )
    signals_for_counter_claim: list[str] = Field(
        min_length=1,
        description="Signal ids that support the counter_claim."
    )
    note: str = Field(
        min_length=10,
        description="1-2 sentences on what kind of conflict this is and why it matters."
    )


class ContextSnapshot(BaseModel):
    """Geographic and cultural context Explorer assumed during this run."""
    geography: Geography = Field(
        description="The geographic frame Explorer used for search and signal interpretation."
    )
    inferred: bool = Field(
        description="True if auto-detected from idea, False if explicitly provided "
                    "via context input."
    )
    confidence: Confidence = Field(
        description="How confident Explorer is in the geography assignment. "
                    "Only meaningful when inferred=True. Set to 'high' when inferred=False."
    )


# ============================================================
# Top-level output model
# ============================================================

class ExplorationResult(BaseModel):
    """Explorer's submitted exploration of the problem space."""

    context_used: ContextSnapshot = Field(
        description="Context Explorer assumed for this run."
    )
    problems: list[AdjacentProblem] = Field(
        min_length=5,
        max_length=8,
        description="5-8 adjacent problems Synthesizer should consider."
    )
    context_constraints: list[ContextConstraint] = Field(
        min_length=1,
        max_length=4,
        description="1-4 constraints that shape viability without being directly solvable."
    )
    signals: list[Signal] = Field(
        min_length=15,
        description="At least 15 user signals, each verbatim with source."
    )
    stakeholders: list[Stakeholder] = Field(
        min_length=3,
        max_length=5,
        description="3-5 stakeholder groups across the full ecosystem."
    )
    assumptions: list[Assumption] = Field(
        min_length=3,
        max_length=7,
        description="3-7 unstated assumptions, each specific, testable, consequential."
    )
    contradictions: list[Contradiction] = Field(
        default_factory=list,
        description="Optional. Structural conflicts between signals. Empty if none found."
    )

    # ----- Validators -----

    @model_validator(mode="after")
    def signals_have_unique_ids(self) -> "ExplorationResult":
        ids = [s.id for s in self.signals]
        if len(ids) != len(set(ids)):
            raise ValueError("Signal ids must be unique within this exploration.")
        return self

    @model_validator(mode="after")
    def at_least_three_distinct_sources(self) -> "ExplorationResult":
        sources = {s.source for s in self.signals}
        if len(sources) < 3:
            raise ValueError(
                f"Signals must come from at least 3 distinct sources. "
                f"Found {len(sources)}."
            )
        return self

    @model_validator(mode="after")
    def no_source_exceeds_forty_percent(self) -> "ExplorationResult":
        total = len(self.signals)
        counts = Counter(s.source for s in self.signals)
        max_share = max(counts.values()) / total
        if max_share > 0.4:
            top_source, top_count = counts.most_common(1)[0]
            raise ValueError(
                f"No single source may contribute more than 40% of signals. "
                f"Source '{top_source}' has {top_count}/{total} ({max_share:.0%})."
            )
        return self

    @model_validator(mode="after")
    def stakeholders_cover_three_types(self) -> "ExplorationResult":
        types = {s.type for s in self.stakeholders}
        if len(types) < 3:
            raise ValueError(
                f"Stakeholder list must include at least 3 distinct type values. "
                f"Found {len(types)}: {sorted(types)}."
            )
        return self

    @model_validator(mode="after")
    def contradiction_signal_refs_valid(self) -> "ExplorationResult":
        valid_ids = {s.id for s in self.signals}
        for i, c in enumerate(self.contradictions):
            all_refs = c.signals_for_claim + c.signals_for_counter_claim
            invalid = [ref for ref in all_refs if ref not in valid_ids]
            if invalid:
                raise ValueError(
                    f"Contradiction #{i} references unknown signal ids: {invalid}"
                )
        return self
