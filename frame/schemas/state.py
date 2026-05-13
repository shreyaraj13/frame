"""Top-level FrameState passed between supervisor turns."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from frame.schemas.critique import Critique
from frame.schemas.evidence import EvidenceCorpus
from frame.schemas.exploration import ExplorationResult
from frame.schemas.package import PMPackage
from frame.schemas.problem import ProblemCandidates, ProblemStatement
from frame.schemas.solution import (
    KilledSolution,
    PrioritizationResult,
    Solution,
    SolutionOptions,
)


class Phase(str, Enum):
    INIT = "init"
    EXPLORING = "exploring"
    SYNTHESIZING = "synthesizing"
    GATE_1 = "gate_1"
    IDEATING = "ideating"
    PRIORITIZING = "prioritizing"
    GATE_2 = "gate_2"
    DEFINING = "defining"
    CRITIQUING = "critiquing"
    DONE = "done"


class EntryMode(str, Enum):
    """The 7 entry points from the spec."""

    IDEA_ONLY = "idea_only"
    IDEA_PLUS_EVIDENCE = "idea_plus_evidence"
    EVIDENCE_ONLY = "evidence_only"
    LOCKED_PROBLEM = "locked_problem"
    LOCKED_PROBLEM_AND_SOLUTION = "locked_problem_and_solution"
    DRAFT_PRD = "draft_prd"
    RESUME_FROM_VAULT = "resume_from_vault"


class FrameState(BaseModel):
    """The single source of truth that flows through the supervisor loop.

    Serialized to .frame_state.json for resume. Whenever a phase mutates state,
    it returns the updated state and the supervisor writes the snapshot.
    """

    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:8]}")
    started_at: datetime = Field(default_factory=datetime.now)
    entry_mode: EntryMode
    phase: Phase = Phase.INIT

    seed_idea: str | None = None
    evidence: EvidenceCorpus | None = None

    exploration: ExplorationResult | None = None
    problem_candidates: ProblemCandidates | None = None
    locked_problem: ProblemStatement | None = None

    solution_options: SolutionOptions | None = None
    prioritization: PrioritizationResult | None = None
    locked_solution: Solution | None = None
    killed_solutions: list[KilledSolution] = Field(default_factory=list)

    package: PMPackage | None = None
    critique: Critique | None = None

    vault_path: Path | None = None
    trace_id: str | None = None

    decision_log: list[str] = Field(default_factory=list)
    """Append every gate decision and phase transition for audit + vault."""

    def snapshot(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Path) -> FrameState:
        return cls.model_validate_json(path.read_text())
