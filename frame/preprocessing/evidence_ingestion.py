"""Parse evidence files into a normalized EvidenceCorpus.

Phase 1 stub: signature in place. Phase 2 implements parsing for
markdown, text, CSV, JSON. PDF is V2.
"""

from __future__ import annotations

from pathlib import Path

from frame.schemas.evidence import EvidenceCorpus


def ingest(paths: list[Path]) -> EvidenceCorpus:
    """STUB — returns empty corpus."""
    raise NotImplementedError("evidence ingestion not wired in Phase 1")
