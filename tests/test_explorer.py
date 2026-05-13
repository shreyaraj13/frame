"""Explorer tests.

- happy_path:        real Claude + Tavily, India JEE idea, asserts ExplorationResult minimums
- with_evidence:     real Claude + Tavily, B2B release-notes idea + seeded evidence,
                     asserts at least one outside-evidence search occurred
- malformed_submit:  unit test with a fake Anthropic client; Claude submits a payload
                     that violates the at-least-three-distinct-sources validator;
                     pydantic.ValidationError must propagate out of explorer.run

==============================================================================
COST WARNING (real money)
==============================================================================
The two `@pytest.mark.integration` tests hit real Anthropic + Tavily APIs.
Per-run estimates (Claude Sonnet 4.6 + Tavily advanced search, observed 2026-05-14):
  - test_explorer_happy_path:     ~$0.20-0.40 Anthropic, ~6 Tavily calls, ~3-5 min
  - test_explorer_with_evidence:  ~$0.20-0.40 Anthropic, ~6 Tavily calls, ~3-5 min
  - Combined `make test-integration`: ~$0.40-0.80, ~7-8 min wall clock

Integration tests are OFF by default in `pyproject.toml` (`addopts = "-m 'not integration'"`).
Run them ONLY via:
  - `make test-integration`   (explicit Makefile target)
  - `pytest -m integration --override-ini="addopts="`  (explicit marker override)

A plain `pytest` or `make test` will NEVER run them — that's intentional. See
~/.claude/CLAUDE.md "Cost discipline" and feedback_cost_discipline memory.
==============================================================================
"""

from __future__ import annotations

import os
from typing import Any

import pytest
from pydantic import ValidationError

from frame.schemas.evidence import EvidenceCorpus, EvidenceItem, EvidenceSource
from frame.schemas.state import EntryMode, FrameState
from frame.subagents import explorer


_INTEGRATION_KEYS_PRESENT = bool(
    os.getenv("ANTHROPIC_API_KEY") and os.getenv("TAVILY_API_KEY")
)


# ============================================================
# Integration tests
# ============================================================


@pytest.mark.integration
@pytest.mark.skipif(
    not _INTEGRATION_KEYS_PRESENT,
    reason="requires ANTHROPIC_API_KEY and TAVILY_API_KEY",
)
async def test_explorer_happy_path() -> None:
    """India-context JEE idea, no evidence. ExplorationResult must meet minimums."""
    state = FrameState(
        entry_mode=EntryMode.IDEA_ONLY,
        seed_idea=(
            "An AI tutor for JEE aspirants that adapts to each student's weak topics."
        ),
    )
    result = await explorer.run(state)

    # Schema minimums (also enforced by Pydantic — these are redundant but explicit).
    assert len(result.problems) >= 5
    assert len(result.signals) >= 15
    assert len(result.stakeholders) >= 3
    assert len(result.assumptions) >= 3

    # Diversity rules.
    distinct_sources = {s.source for s in result.signals}
    assert len(distinct_sources) >= 3, f"only {len(distinct_sources)} sources: {distinct_sources}"

    distinct_stakeholder_types = {s.type for s in result.stakeholders}
    assert len(distinct_stakeholder_types) >= 3, distinct_stakeholder_types


@pytest.mark.integration
@pytest.mark.skipif(
    not _INTEGRATION_KEYS_PRESENT,
    reason="requires ANTHROPIC_API_KEY and TAVILY_API_KEY",
)
async def test_explorer_with_evidence() -> None:
    """B2B release-notes idea + seeded evidence. Must probe outside the evidence frame."""
    evidence = EvidenceCorpus(
        items=[
            EvidenceItem(
                text="Our team always punts on writing release notes after a sprint.",
                source=EvidenceSource.USER_INTERVIEW,
                source_label="eng-interview-1",
            ),
            EvidenceItem(
                text="Customers email us asking what actually changed in the last release.",
                source=EvidenceSource.SUPPORT_TICKET,
                source_label="ticket-001",
            ),
            EvidenceItem(
                text="Release notes are always written 2 days after the release ships.",
                source=EvidenceSource.USER_INTERVIEW,
                source_label="eng-interview-2",
            ),
            EvidenceItem(
                text="PMs hate writing changelogs; engineers hate writing them more.",
                source=EvidenceSource.USER_INTERVIEW,
                source_label="pm-interview-1",
            ),
            EvidenceItem(
                text="Three different release-note formats across three teams.",
                source=EvidenceSource.INTERNAL_DOC,
                source_label="internal-wiki",
            ),
        ]
    )
    state = FrameState(
        entry_mode=EntryMode.IDEA_PLUS_EVIDENCE,
        seed_idea=(
            "A tool that auto-generates release notes from Git history for engineering teams."
        ),
        evidence=evidence,
    )

    trace: list[dict[str, Any]] = []
    result = await explorer.run(state, tool_trace=trace)

    assert len(result.signals) >= 15

    # At least one search must probe outside the evidence's frame (rule #8 in the prompt).
    #
    # The evidence we seeded is producer-centric (engineers/PMs struggling to *write*
    # release notes for a single team). An outside-view query is one that introduces
    # a perspective the evidence does NOT cover. For THIS test idea + evidence pair,
    # those perspectives include:
    #   - named competitors / alternatives in the release-notes tooling space
    #   - reader/consumer perspective (end users, audience of release notes)
    #   - cross-team adoption dynamics (resistance to process change)
    #
    # These markers are intentionally specific to this test case. Different ideas
    # need different markers; do NOT extract this list into a shared helper. The
    # purpose is to verify Explorer *probed* outside the evidence, not to define
    # "outside-view" globally.
    outside_view_markers = (
        "semantic-release", "release-drafter", "git-cliff",
        "end user", "end-user", "audience", "don't read",
        "adoption resistance", "buy-in",
    )
    search_queries = [
        (e["input"].get("query") or "").lower()
        for e in trace
        if e["name"] in ("web_search_user_signals", "fetch_forum_threads") and e["ok"]
    ]
    hits_outside_view = any(
        any(marker in q for marker in outside_view_markers)
        for q in search_queries
    )
    assert hits_outside_view, (
        "Expected at least one search query to hit an outside-evidence-view marker.\n"
        f"Markers checked (case-insensitive, substring match): {outside_view_markers}\n"
        f"All search queries: {search_queries}"
    )


# ============================================================
# Unit test: malformed submit_exploration must raise ValidationError
# ============================================================


class _FakeBlock:
    """Minimal stand-in for anthropic.types.ToolUseBlock / TextBlock."""

    def __init__(self, **kwargs: Any) -> None:
        self.type = kwargs.get("type")
        self.name = kwargs.get("name")
        self.input = kwargs.get("input")
        self.id = kwargs.get("id")
        self.text = kwargs.get("text")


class _FakeResponse:
    def __init__(self, content: list[_FakeBlock], stop_reason: str = "tool_use") -> None:
        self.content = content
        self.stop_reason = stop_reason


class _FakeMessages:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)

    async def create(self, **kwargs: Any) -> _FakeResponse:
        if not self._responses:
            raise RuntimeError("FakeMessages out of canned responses")
        return self._responses.pop(0)


class _FakeAnthropic:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self.messages = _FakeMessages(responses)


def _malformed_exploration_payload() -> dict[str, Any]:
    """Build an ExplorationResult payload that violates at_least_three_distinct_sources.

    15 signals are required. We give 15, but only across 2 distinct sources — the
    validator demands 3. Every other validator must pass so this is the failure
    we exercise.
    """
    two_sources = ["https://only-source-a.example", "https://only-source-b.example"]
    signals = [
        {
            "id": f"s{i}",
            "quote": f"This is a long-enough verbatim quote number {i}, with substance.",
            "source": two_sources[i % 2],
            "source_type": "forum",
        }
        for i in range(1, 16)
    ]
    return {
        "context_used": {"geography": "global", "inferred": True, "confidence": "high"},
        "problems": [
            {
                "description": (
                    f"Adjacent problem number {i}, described at length to pass min_length."
                ),
                "relationship_to_idea": "It is in the same neighborhood.",
            }
            for i in range(1, 6)
        ],
        "context_constraints": [
            {
                "description": "A viability-shaping constraint described at sufficient length.",
                "relationship_to_idea": "It shapes deployment cost and timing.",
            }
        ],
        "signals": signals,
        "stakeholders": [
            {
                "name": "Direct users",
                "type": "user",
                "relationship_to_problem": "They feel the pain repeatedly and would adopt.",
            },
            {
                "name": "Buyers",
                "type": "buyer",
                "relationship_to_problem": "They sign cheques and care about return on spend.",
            },
            {
                "name": "Gatekeepers",
                "type": "gatekeeper",
                "relationship_to_problem": "They decide whether the team is allowed to adopt.",
            },
        ],
        "assumptions": [
            {
                "statement": (
                    f"Assumption number {i} is specifically phrased and testable."
                ),
                "why_consequential": "If wrong, the premise collapses for the target user.",
                "criticality": "high",
                "why_critical": "It is load-bearing for the proposed mechanism.",
            }
            for i in range(1, 4)
        ],
        "contradictions": [],
    }


async def test_explorer_malformed_submit() -> None:
    """Claude submits a payload that violates a validator; ValidationError propagates."""
    fake_client = _FakeAnthropic(
        [
            _FakeResponse(
                content=[
                    _FakeBlock(
                        type="tool_use",
                        name="submit_exploration",
                        input=_malformed_exploration_payload(),
                        id="toolu_test_malformed",
                    )
                ],
                stop_reason="tool_use",
            )
        ]
    )

    state = FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea="any test idea")

    with pytest.raises(ValidationError):
        await explorer.run(state, client=fake_client)  # type: ignore[arg-type]
