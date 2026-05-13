"""obsidian-mcp — Phase 1 skeleton.

Starts cleanly on stdio. Tool signatures registered. All bodies raise
NotImplementedError. Phase 2 wires the real vault writes.

Tools planned:
  - write_package        : write a Frame package folder to the vault
  - link_related_notes   : add backlinks across notes in a package
  - attach_metadata      : update YAML frontmatter
  - create_decision_log  : append an entry to the package decision log
  - read_vault_package   : read an existing Frame package back into FrameState

Run with: python -m mcp_servers.obsidian_mcp.server
"""

from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

SERVER_NAME = "obsidian-mcp"
server: Server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="write_package",
            description="STUB — write a Frame package folder to the Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_json": {"type": "string", "description": "PMPackage JSON."},
                    "vault_path": {"type": "string"},
                },
                "required": ["package_json", "vault_path"],
            },
        ),
        Tool(
            name="link_related_notes",
            description="STUB — add backlinks between notes in a package folder.",
            inputSchema={
                "type": "object",
                "properties": {"package_path": {"type": "string"}},
                "required": ["package_path"],
            },
        ),
        Tool(
            name="attach_metadata",
            description="STUB — update YAML frontmatter on a note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_path": {"type": "string"},
                    "metadata": {"type": "object"},
                },
                "required": ["note_path", "metadata"],
            },
        ),
        Tool(
            name="create_decision_log",
            description="STUB — append an entry to the package decision log.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_path": {"type": "string"},
                    "entry": {"type": "string"},
                },
                "required": ["package_path", "entry"],
            },
        ),
        Tool(
            name="read_vault_package",
            description="STUB — read an existing Frame package back into FrameState JSON.",
            inputSchema={
                "type": "object",
                "properties": {"package_path": {"type": "string"}},
                "required": ["package_path"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    raise NotImplementedError(f"{SERVER_NAME}.{name} not wired in Phase 1")


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
