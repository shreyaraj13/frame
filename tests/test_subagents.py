"""Phase 1 sanity: each sub-agent stub returns a valid Pydantic object."""

from __future__ import annotations

import pytest

from frame.schemas.state import EntryMode, FrameState
from frame.subagents import (
    critic,
    definer,
    explorer,
    ideator,
    prioritizer,
    synthesizer,
)


@pytest.fixture
def state() -> FrameState:
    return FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="x")


async def test_explorer_returns_exploration(state: FrameState) -> None:
    result = await explorer.run(state)
    assert result.seed_idea == "x"


async def test_synthesizer_returns_candidates(state: FrameState) -> None:
    result = await synthesizer.run(state)
    assert result.candidates == []


async def test_ideator_returns_options(state: FrameState) -> None:
    result = await ideator.run(state)
    assert result.solutions == []


async def test_prioritizer_returns_result(state: FrameState) -> None:
    result = await prioritizer.run(state)
    assert result.rice_scores == []


async def test_definer_returns_package(state: FrameState) -> None:
    result = await definer.run(state)
    assert result.idea == "x"


async def test_critic_returns_critique(state: FrameState) -> None:
    result = await critic.run(state)
    assert result.ready_to_ship is False
