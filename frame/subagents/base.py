"""Shared sub-agent runner. Each sub-agent is a Claude conversation with its own tools.

Phase 1: stub. Phase 2: real anthropic.AsyncAnthropic client with tool-use loop.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from frame.config import get_settings

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a sub-agent system prompt from frame/prompts/<name>.md."""
    return (PROMPTS_DIR / f"{name}.md").read_text()


async def run_subagent(
    *,
    name: str,
    user_message: str,
    tools: list[dict[str, Any]] | None = None,
    max_iterations: int = 12,
) -> str:
    """Run a sub-agent loop. Phase 1 stub returns the prompt name; Phase 2 wires Claude.

    The Phase 2 implementation:
      1. Load system prompt via load_prompt(name).
      2. Open AsyncAnthropic stream with tools=[...].
      3. Loop: if response has tool_use blocks, dispatch each to the local
         tool registry, append tool_result, continue. Else return text.
      4. Cap at max_iterations to fail loud on tool-call loops.
    """

    _ = get_settings()  # ensure config loads; Phase 2 will use it.
    return f"[stub:{name}] would handle: {user_message[:80]}"
