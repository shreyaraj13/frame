"""Phase 1 placeholder for the full-pipeline DeepEval test.

Phase 2: load golden_ideas.json, run supervisor end-to-end against each,
score outputs against rubric files in evals/rubrics/, fail on regression.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Phase 1 — pipeline test arrives with the first real agent")
def test_full_pipeline_placeholder() -> None:
    raise NotImplementedError("eval pipeline not wired in Phase 1")
