"""MCP servers for Frame.

Phase 1: skeletons only — each server starts cleanly on stdio and exposes
its tool signatures, but every tool body raises NotImplementedError.

obsidian_mcp is the only server we currently plan to ship as a real MCP
server (reusable from Claude Desktop). The 6 sub-agent MCP directories
exist so the option to promote one to MCP stays open.
"""
