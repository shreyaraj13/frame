"""explorer-mcp — Phase 1 skeleton (optional; sub-agent may stay inline)."""

from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

SERVER_NAME = "explorer-mcp"
server: Server = Server(SERVER_NAME)

TOOL_NAMES = [
    "web_search_user_signals",
    "fetch_forum_threads",
    "map_stakeholders",
    "surface_assumptions",
    "ingest_evidence",
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=name,
            description=f"STUB — {name}",
            inputSchema={"type": "object", "properties": {}},
        )
        for name in TOOL_NAMES
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    raise NotImplementedError(f"{SERVER_NAME}.{name} not wired in Phase 1")


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
