"""Phase 1 sanity: preprocessing stubs raise NotImplementedError cleanly."""

from __future__ import annotations

from pathlib import Path

import pytest

from frame.preprocessing.clustering import cluster
from frame.preprocessing.embedding import embed
from frame.preprocessing.evidence_ingestion import ingest
from frame.schemas.evidence import EvidenceCorpus


def test_ingest_stubbed() -> None:
    with pytest.raises(NotImplementedError):
        ingest([Path("nope.md")])


def test_embed_stubbed() -> None:
    with pytest.raises(NotImplementedError):
        embed(["hello"])


def test_cluster_stubbed() -> None:
    with pytest.raises(NotImplementedError):
        cluster(EvidenceCorpus(), None)
