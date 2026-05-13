"""explorer-mcp — runnable MCP server over the canonical tool implementations.

Imports `tools.py` (single source of truth) and registers MCP wrappers so the
same 6 tools are callable from Claude Desktop / Cursor / any MCP client. The
in-process supervisor pipeline does NOT use this server — explorer.py imports
tools.py directly. This server exists for external reuse and portfolio demo.

Note: the MCP-side `ingest_evidence` takes a corpus JSON as input because the
server has no FrameState. The Anthropic schema in tools.py takes no input
because the inline dispatch reads from state.evidence directly.

Run with: python -m mcp_servers.explorer_mcp.server
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from frame.schemas.evidence import EvidenceCorpus
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

SERVER_NAME = "explorer-mcp"
server: Server = Server(SERVER_NAME)


# Map Anthropic tool names → MCP-side input_schema. Most are identical;
# ingest_evidence is the one that diverges because MCP has no implicit state.
_MCP_INPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "ingest_evidence": {
        "type": "object",
        "properties": {
            "corpus": {
                "type": "object",
                "description": (
                    "Pre-parsed EvidenceCorpus JSON (items + clusters + "
                    "clustering_method). Pass null/omit for an empty pass-through."
                ),
            },
        },
    },
}


def _input_schema_for(tool_name: str, anthropic_schema: dict[str, Any]) -> dict[str, Any]:
    return _MCP_INPUT_SCHEMAS.get(tool_name, anthropic_schema)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=spec["name"],
            description=spec["description"],
            inputSchema=_input_schema_for(spec["name"], spec["input_schema"]),
        )
        for spec in ANTHROPIC_TOOLS
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        result = _dispatch(name, arguments)
    except ToolError as e:
        return [TextContent(type="text", text=f"ToolError: {e}")]
    except Exception as e:  # noqa: BLE001 — surface anything else to the client
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]

    if hasattr(result, "model_dump_json"):
        payload = result.model_dump_json(indent=2)  # type: ignore[union-attr]
    else:
        payload = json.dumps(result, indent=2, default=str)
    return [TextContent(type="text", text=payload)]


def _dispatch(name: str, arguments: dict[str, Any]) -> Any:
    if name == "web_search_user_signals":
        return web_search_user_signals(**arguments)
    if name == "fetch_forum_threads":
        return fetch_forum_threads(**arguments)
    if name == "ingest_evidence":
        raw = arguments.get("corpus")
        corpus = EvidenceCorpus.model_validate(raw) if raw else None
        return ingest_evidence(corpus)
    if name == "map_stakeholders":
        return map_stakeholders(**arguments)
    if name == "surface_assumptions":
        return surface_assumptions(**arguments)
    if name == "submit_exploration":
        return submit_exploration(arguments)
    raise ToolError(f"Unknown tool: {name}")


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
