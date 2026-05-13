"""Phase 1 sanity: tool stubs are callable and return the expected stub values."""

from __future__ import annotations

from frame.schemas.state import EntryMode, FrameState
from frame.tools.gates import GateAction, GateChoice, continuation_prompt, present_gate_to_user
from frame.tools.vault import package_dir, write_package


def test_gate_returns_hardcoded_pick() -> None:
    decision = present_gate_to_user(
        title="test",
        choices=[GateChoice(label="a"), GateChoice(label="b")],
        recommendation_index=0,
    )
    assert decision.action == GateAction.PICK
    assert decision.picked_index == 0


def test_continuation_returns_continue() -> None:
    assert continuation_prompt("next") == "continue"


def test_vault_package_dir_is_pure() -> None:
    state = FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="hello")
    target = package_dir(state)
    assert "Frame Packages" in str(target)
    assert "hello" in target.name


def test_vault_write_does_not_create_files(tmp_path) -> None:
    state = FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="hello")
    target = write_package(state)
    # Phase 1 stub must not actually write.
    assert not target.exists() or target.is_dir()  # we never created it
