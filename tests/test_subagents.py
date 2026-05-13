"""Sanity: each sub-agent stub returns a valid Pydantic object.

Explorer is now real and tested in tests/test_explorer.py — it's not
included here because (a) it needs API keys and (b) the malformed-submit
case is exercised there with a fake client.
"""

from __future__ import annotations

import pytest

from frame.schemas.state import EntryMode, FrameState
from frame.subagents import (
    critic,
    definer,
    ideator,
    prioritizer,
    synthesizer,
)


@pytest.fixture
def state() -> FrameState:
    return FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="x")


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
