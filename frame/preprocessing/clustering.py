"""HDBSCAN clustering with sampling fallback — Phase 1 stub.

Phase 2 wires HDBSCAN + min_cluster_size + noise-ratio fallback path.
"""

from __future__ import annotations

from frame.schemas.evidence import EvidenceCorpus


def cluster(corpus: EvidenceCorpus, embeddings) -> EvidenceCorpus:  # noqa: ARG001
    """STUB — Phase 2 returns corpus with .clusters populated."""
    raise NotImplementedError("clustering not wired in Phase 1")
