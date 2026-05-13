"""Explorer sub-agent — problem-space divergence.

Real Claude tool-use loop. Imports canonical tool impls from
mcp_servers/explorer_mcp/tools.py (inline Python dispatch, no stdio).

Termination contract:
  - submit_exploration with valid input → return ExplorationResult
  - submit_exploration with invalid input → pydantic.ValidationError propagates
    (strict; explorer.run does NOT catch + retry. To relax, wrap the call site.)
  - end_turn without submit_exploration → ExplorerProtocolError
  - MAX_ITERATIONS reached → ExplorerProtocolError

==============================================================================
COST WARNING (real money — read before invoking)
==============================================================================
Each `explorer.run()` call against the real Anthropic + Tavily APIs costs
roughly $0.20-0.40 (Claude Sonnet 4.6) + ~3-6 Tavily searches, and takes 3-5
minutes wall clock. Do not invoke from background scripts, batch jobs, or
loops without explicit user consent. See ~/.claude/CLAUDE.md "Cost discipline".

Test-time injection: pass `client=<fake_anthropic>` to skip the real API.
==============================================================================
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic

from frame.config import get_settings
from frame.schemas.evidence import EvidenceCorpus
from frame.schemas.exploration import ExplorationResult
from frame.schemas.state import FrameState
from mcp_servers.explorer_mcp.tools import (
    ANTHROPIC_TOOLS,
    ToolError,
    fetch_forum_threads,
    ingest_evidence,
    map_stakeholders,
    submit_exploration,
    surface_assumptions,
    web_search_user_signals,
)

log = logging.getLogger(__name__)

MAX_ITERATIONS = 30

# Web search budget — shared by web_search_user_signals + fetch_forum_threads.
# Mirrors hard rule #3 in frame/prompts/explorer.md. Enforced in code so a
# prompt-following lapse can't blow past it.
SEARCH_BUDGET = 6
SEARCH_TOOLS = {"web_search_user_signals", "fetch_forum_threads"}

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "explorer.md"


class ExplorerProtocolError(RuntimeError):
    """Raised when Explorer violates the tool-use contract."""


def _load_prompt() -> str:
    return PROMPT_PATH.read_text()


def _format_initial_user_message(state: FrameState) -> str:
    parts: list[str] = [f"idea: {state.seed_idea or '(no seed idea provided)'}"]
    if state.evidence and state.evidence.items:
        parts.append(
            f"evidence: provided ({len(state.evidence.items)} items). "
            "Call ingest_evidence to read."
        )
    else:
        parts.append("evidence: none provided")
    return "\n".join(parts)


def _dispatch_tool(
    name: str,
    tool_input: dict[str, Any],
    state: FrameState,
) -> Any:
    if name == "web_search_user_signals":
        return web_search_user_signals(**tool_input)
    if name == "fetch_forum_threads":
        return fetch_forum_threads(**tool_input)
    if name == "ingest_evidence":
        return ingest_evidence(state.evidence)
    if name == "map_stakeholders":
        return map_stakeholders(**tool_input)
    if name == "surface_assumptions":
        return surface_assumptions(**tool_input)
    raise ToolError(f"Unknown tool: {name}")


def _record(
    trace: list[dict[str, Any]] | None,
    name: str,
    tool_input: dict[str, Any],
    ok: bool,
    error: str | None = None,
) -> None:
    if trace is not None:
        trace.append({"name": name, "input": tool_input, "ok": ok, "error": error})


async def run(
    state: FrameState,
    *,
    evidence: EvidenceCorpus | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
    client: AsyncAnthropic | None = None,
) -> ExplorationResult:
    """Run Explorer end-to-end. Returns a validated ExplorationResult.

    Args:
      state: FrameState carrying the seed idea and optional evidence.
      evidence: optional override; if provided, replaces state.evidence in-place.
      tool_trace: optional list that captures every tool call as
        {"name", "input", "ok", "error"}. Production callers pass None;
        tests use this to assert search-query coverage.
      client: optional pre-built AsyncAnthropic (used by unit tests to inject a mock).
    """

    if evidence is not None:
        state.evidence = evidence

    settings = get_settings()
    client_owned = False
    if client is None:
        if not settings.anthropic_api_key:
            raise ExplorerProtocolError(
                "ANTHROPIC_API_KEY is not set. Explorer cannot run."
            )
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        client_owned = True

    try:
        system_prompt = _load_prompt()
        initial_user = _format_initial_user_message(state)
        messages: list[dict[str, Any]] = [{"role": "user", "content": initial_user}]
        search_count = 0  # combined budget across SEARCH_TOOLS, enforced per SEARCH_BUDGET

        for iteration in range(MAX_ITERATIONS):
            response = await client.messages.create(
                model=settings.model,
                max_tokens=settings.max_tokens,
                system=system_prompt,
                tools=ANTHROPIC_TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            tool_results: list[dict[str, Any]] = []
            final_result: ExplorationResult | None = None

            for block in response.content:
                if getattr(block, "type", None) != "tool_use":
                    continue

                tool_name = block.name
                tool_input = dict(block.input or {})
                tool_id = block.id

                if tool_name == "submit_exploration":
                    # Strict: ValidationError propagates out of run().
                    _record(tool_trace, tool_name, tool_input, ok=True)
                    final_result = submit_exploration(tool_input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": "Exploration accepted.",
                        }
                    )
                    continue

                # Search-budget enforcement: web_search_user_signals and
                # fetch_forum_threads share a single SEARCH_BUDGET. The 7th attempt
                # gets surfaced to Claude as a tool error telling it to wrap up.
                if tool_name in SEARCH_TOOLS:
                    if search_count >= SEARCH_BUDGET:
                        _record(
                            tool_trace, tool_name, tool_input,
                            ok=False, error="search_budget_exhausted",
                        )
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": (
                                    f"Search budget exhausted ({SEARCH_BUDGET}/"
                                    f"{SEARCH_BUDGET}). Call submit_exploration now."
                                ),
                                "is_error": True,
                            }
                        )
                        continue
                    search_count += 1

                try:
                    result = _dispatch_tool(tool_name, tool_input, state)
                    payload = (
                        result.model_dump_json()
                        if hasattr(result, "model_dump_json")
                        else json.dumps(result, default=str)
                    )
                    _record(tool_trace, tool_name, tool_input, ok=True)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tool_id, "content": payload}
                    )
                except ToolError as e:
                    _record(tool_trace, tool_name, tool_input, ok=False, error=str(e))
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"ToolError: {e}",
                            "is_error": True,
                        }
                    )
                except Exception as e:  # noqa: BLE001 — surface synthesis validation errors etc.
                    _record(tool_trace, tool_name, tool_input, ok=False, error=str(e))
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"{type(e).__name__}: {e}",
                            "is_error": True,
                        }
                    )

            if final_result is not None:
                return final_result

            if response.stop_reason == "end_turn":
                raise ExplorerProtocolError(
                    "Claude ended turn without calling submit_exploration."
                )

            if not tool_results:
                raise ExplorerProtocolError(
                    f"stop_reason={response.stop_reason} with no tool calls — protocol break."
                )

            messages.append({"role": "user", "content": tool_results})

        raise ExplorerProtocolError(
            f"Reached MAX_ITERATIONS={MAX_ITERATIONS} without submit_exploration."
        )
    finally:
        # Only close clients we created; injected clients (tests) stay owned by caller.
        if client_owned and hasattr(client, "close"):
            try:
                await client.close()
            except Exception:  # noqa: BLE001 — cleanup must not mask real errors
                pass
