"""Evidence ingestion schemas — first-class input to Frame.

Every problem statement and solution references evidence_ids back to
items in an EvidenceCorpus, preserving traceability from PRD claims to raw input.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    USER_INTERVIEW = "user_interview"
    REVIEW = "review"
    SUPPORT_TICKET = "support_ticket"
    FORUM_POST = "forum_post"
    SURVEY = "survey"
    ANALYTICS = "analytics"
    INTERNAL_DOC = "internal_doc"
    OTHER = "other"


class EvidenceItem(BaseModel):
    """One atomic piece of evidence. Normalized from CSV/JSON/MD/TXT."""

    id: str = Field(default_factory=lambda: f"ev_{uuid4().hex[:8]}")
    text: str
    source: EvidenceSource = EvidenceSource.OTHER
    source_label: str | None = None
    """e.g., 'App Store reviews, Mar 2026' — verbatim from filename or user tag."""
    timestamp: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class EvidenceCluster(BaseModel):
    """Output of HDBSCAN clustering — a theme found in the corpus."""

    cluster_id: int
    representative_items: list[str]
    """EvidenceItem.id values closest to the cluster centroid."""
    frequency: int
    """Number of items in this cluster — passed to the LLM as theme weight."""
    summary: str | None = None


class EvidenceCorpus(BaseModel):
    """Bundle of evidence + any clustering applied."""

    items: list[EvidenceItem] = Field(default_factory=list)
    clusters: list[EvidenceCluster] = Field(default_factory=list)
    clustering_method: str | None = None
    """e.g., 'hdbscan' or 'sampling-fallback'."""

    def get(self, item_id: str) -> EvidenceItem | None:
        return next((i for i in self.items if i.id == item_id), None)
