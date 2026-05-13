"""Explorer's 6 tools — canonical implementations + Anthropic tool schemas.

Single source of truth: `frame/subagents/explorer.py` imports and dispatches
these. `mcp_servers/explorer_mcp/server.py` registers MCP wrappers around the
same functions so the tools are also runnable as a standalone MCP server.

Tools:
  - web_search_user_signals : Tavily web search
  - fetch_forum_threads     : Tavily with reddit/HN/lobsters site filters
  - ingest_evidence         : pass-through over a pre-parsed EvidenceCorpus
  - map_stakeholders        : validates a draft stakeholder list (no I/O)
  - surface_assumptions     : validates a draft assumption list (no I/O)
  - submit_exploration      : validates the final ExplorationResult
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import BaseModel
from tavily import TavilyClient

from frame.config import get_settings
from frame.schemas.evidence import EvidenceCorpus
from frame.schemas.exploration import (
    Assumption,
    ExplorationResult,
    Stakeholder,
)


# ============================================================
# Errors
# ============================================================

class ToolError(RuntimeError):
    """Raised when a tool fails in a way that should surface to Claude as is_error."""


# ============================================================
# Defaults
# ============================================================

DEFAULT_FORUM_SITES: list[str] = [
    "reddit.com",
    "news.ycombinator.com",
    "lobste.rs",
]

# Cap Tavily content snippets so we don't blow up the model context.
SNIPPET_MAX_CHARS = 500

# Tavily retry policy: one retry, only for transport/5xx-flavored errors.
TAVILY_RETRY_ATTEMPTS = 2

# Tokens in an error message that should surface immediately without retry.
_NON_RETRY_TOKENS = ("rate", "429", "401", "403", "402", "quota", "unauthorized")


# ============================================================
# Tavily wrapper
# ============================================================

def _tavily_search(
    query: str,
    *,
    max_results: int = 10,
    sites: list[str] | None = None,
) -> dict[str, Any]:
    """Single Tavily call with retry-on-5xx and surface-on-4xx semantics."""

    settings = get_settings()
    if not settings.tavily_api_key:
        raise ToolError("TAVILY_API_KEY is not set; cannot perform web search.")

    client = TavilyClient(api_key=settings.tavily_api_key)
    kwargs: dict[str, Any] = {
        "query": query,
        "max_results": min(max(int(max_results), 1), 20),
        "search_depth": "advanced",
    }
    if sites:
        kwargs["include_domains"] = list(sites)

    last_err: Exception | None = None
    for _ in range(TAVILY_RETRY_ATTEMPTS):
        try:
            raw = client.search(**kwargs)
        except Exception as e:  # noqa: BLE001 — Tavily client surfaces varied exception types
            msg = str(e).lower()
            if any(tok in msg for tok in _NON_RETRY_TOKENS):
                raise ToolError(f"Tavily client error (not retried): {e}") from e
            last_err = e
            continue
        return {
            "query": raw.get("query", query),
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": (r.get("content") or "")[:SNIPPET_MAX_CHARS],
                }
                for r in raw.get("results", [])
            ],
        }

    raise ToolError(f"Tavily search failed after {TAVILY_RETRY_ATTEMPTS} attempts: {last_err}")


# ============================================================
# Tool implementations
# ============================================================

def web_search_user_signals(query: str, max_results: int = 10) -> dict[str, Any]:
    """General Tavily web search."""
    return _tavily_search(query, max_results=max_results)


def fetch_forum_threads(query: str, sites: list[str] | None = None) -> dict[str, Any]:
    """Tavily search restricted to forum sites (reddit/HN/lobsters by default)."""
    effective_sites = sites if sites else DEFAULT_FORUM_SITES
    return _tavily_search(query, sites=effective_sites)


def ingest_evidence(corpus: EvidenceCorpus | None) -> dict[str, Any]:
    """Format a pre-parsed evidence corpus for Claude to cite.

    Real file parsing arrives in preprocessing (Phase 2 step 9). This tool
    only surfaces what's already on state.evidence.
    """
    if corpus is None or not corpus.items:
        return {"items": [], "clusters": [], "note": "No evidence provided in this run."}

    items = [
        {
            "id": item.id,
            "text": item.text,
            "source_label": item.source_label,
            "source_type": item.source.value,
            "metadata": item.metadata,
        }
        for item in corpus.items
    ]
    clusters = [c.model_dump(mode="json") for c in corpus.clusters]
    return {
        "items": items,
        "clusters": clusters,
        "clustering_method": corpus.clustering_method,
        "item_count": len(items),
    }


def map_stakeholders(stakeholders: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate a draft stakeholder list. No I/O — synthesis support.

    Errors here surface to Claude so it can fix the shape before submit_exploration.
    """
    validated = [Stakeholder.model_validate(s) for s in stakeholders]
    return {
        "validated_stakeholders": [s.model_dump(mode="json") for s in validated],
        "count": len(validated),
        "type_coverage": sorted({s.type for s in validated}),
    }


def surface_assumptions(assumptions: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate a draft assumption list. No I/O — synthesis support."""
    validated = [Assumption.model_validate(a) for a in assumptions]
    return {
        "validated_assumptions": [a.model_dump(mode="json") for a in validated],
        "count": len(validated),
        "criticality_distribution": dict(
            Counter(a.criticality for a in validated)
        ),
    }


def submit_exploration(payload: dict[str, Any]) -> ExplorationResult:
    """Validate the final ExplorationResult.

    STRICT: raises pydantic.ValidationError on bad input. Explorer's loop
    propagates the error rather than feeding it back to Claude. If we later
    want retry semantics, wrap the call site, not this function.
    """
    return ExplorationResult.model_validate(payload)


# ============================================================
# Anthropic tool schemas
# ============================================================

class _MapStakeholdersInput(BaseModel):
    stakeholders: list[Stakeholder]


class _SurfaceAssumptionsInput(BaseModel):
    assumptions: list[Assumption]


ANTHROPIC_TOOLS: list[dict[str, Any]] = [
    {
        "name": "web_search_user_signals",
        "description": (
            "Web search via Tavily for verbatim user signals, complaints, and "
            "discussions related to a query. Returns a list of results with title, "
            "URL, and snippet. For India-context runs, anchor your query to India "
            "(named cities, named competitors, named subreddits)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results to return (1-20, default 10).",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_forum_threads",
        "description": (
            "Search forum/community sites (Reddit, HN, Lobsters by default) via "
            "Tavily site filters. Use when you specifically want forum discussions "
            "rather than blog posts or news. Override the default site list via "
            "`sites` if a specific subreddit or community is more relevant."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "sites": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional site filter list, e.g. "
                        f"{DEFAULT_FORUM_SITES}. Defaults to reddit + HN + lobsters."
                    ),
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "ingest_evidence",
        "description": (
            "Read the pre-parsed user evidence (if any) on this run's input. "
            "Returns items with verbatim text, source labels, and any cluster "
            "structure already attached. Call this once at the start if evidence "
            "was provided. Returns an empty list with a note if none."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "map_stakeholders",
        "description": (
            "Submit a draft stakeholder list for schema validation. Pure synthesis — "
            "no web calls. Use this BEFORE submit_exploration to confirm your "
            "stakeholder shape will pass validation. Returns type coverage so you "
            "can verify the 3-distinct-types rule before final submit."
        ),
        "input_schema": _MapStakeholdersInput.model_json_schema(),
    },
    {
        "name": "surface_assumptions",
        "description": (
            "Submit a draft assumption list for schema validation. Pure synthesis — "
            "no web calls. Returns a criticality distribution so you can sanity-check "
            "your rankings before submit_exploration."
        ),
        "input_schema": _SurfaceAssumptionsInput.model_json_schema(),
    },
    {
        "name": "submit_exploration",
        "description": (
            "Submit your final ExplorationResult. Call exactly ONCE at the end of "
            "the run. The schema enforces hard rules: 5-8 problems, 1-4 context "
            "constraints, 15+ signals from 3+ distinct sources (no source over "
            "40%), 3-5 stakeholders covering 3+ distinct types, 3-7 assumptions. "
            "Bad submissions raise ValidationError and end the run — no retry."
        ),
        "input_schema": ExplorationResult.model_json_schema(),
    },
]
