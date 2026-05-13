"""Phase 1 sanity tests for FrameState — Phase 2 adds more."""

from __future__ import annotations

from pathlib import Path

from frame.schemas.state import EntryMode, FrameState, Phase


def test_state_roundtrip(tmp_path: Path) -> None:
    state = FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="test idea")
    state.decision_log.append("init")

    snap = tmp_path / "state.json"
    state.snapshot(snap)
    loaded = FrameState.load(snap)

    assert loaded.entry_mode == EntryMode.IDEA_ONLY
    assert loaded.seed_idea == "test idea"
    assert loaded.decision_log == ["init"]


def test_initial_phase_is_init() -> None:
    state = FrameState(entry_mode=EntryMode.IDEA_ONLY)
    assert state.phase == Phase.INIT
