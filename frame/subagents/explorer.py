"""Explorer sub-agent — problem-space divergence.

Soft targets: 5+ adjacent problems, 15+ user signals. Stops by judgment.
Can accept raw evidence as primary signal source.
"""

from __future__ import annotations

from frame.schemas.evidence import EvidenceCorpus
from frame.schemas.exploration import ExplorationResult
from frame.schemas.state import FrameState
from frame.subagents.base import run_subagent


async def run(state: FrameState, evidence: EvidenceCorpus | None = None) -> ExplorationResult:
    """Run the Explorer. Phase 1 stub returns an empty result with the seed idea."""

    seed = state.seed_idea or "(no seed idea yet)"
    _ = await run_subagent(name="explorer", user_message=f"Explore: {seed}")

    return ExplorationResult(
        seed_idea=seed,
        used_evidence=evidence is not None and len(evidence.items) > 0,
    )
