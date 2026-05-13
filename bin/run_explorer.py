"""Run Explorer against a single product idea and print the ExplorationResult.

==============================================================================
COST WARNING (real money — read before invoking)
==============================================================================
This script makes a real Anthropic + Tavily call. Estimated per-run cost:
  ~$0.20-0.40 Claude Sonnet 4.6 + ~3-6 Tavily searches, 3-5 min wall clock.

Per cost-discipline rules (~/.claude/CLAUDE.md), this script REQUIRES an
explicit --confirm flag. Without it, the script refuses to run.

Usage:
  uv run python bin/run_explorer.py "Your idea here" --confirm
  # or via Make:
  make explore IDEA="Your idea here" CONFIRM=yes
==============================================================================
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from frame.schemas.state import EntryMode, FrameState
from frame.subagents.explorer import run


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="run_explorer",
        description="Run Explorer against a single product idea.",
    )
    p.add_argument("idea", help="Product idea, as a single sentence string.")
    p.add_argument(
        "--confirm",
        action="store_true",
        help="REQUIRED. Confirms you authorize the paid API call.",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Optional path to write the full JSON ExplorationResult (in addition to stdout).",
    )
    return p.parse_args()


async def _main(idea: str, out_path: str | None) -> int:
    state = FrameState(entry_mode=EntryMode.IDEA_ONLY, seed_idea=idea)
    result = await run(state)
    payload = result.model_dump_json(indent=2)
    print(payload)
    if out_path:
        with open(out_path, "w") as f:
            f.write(payload)
    return 0


def main() -> int:
    args = parse_args()
    if not args.confirm:
        print(
            "REFUSED: cost-discipline guard.\n"
            "Re-run with --confirm to authorize the paid API call "
            "(~$0.30 Claude + ~6 Tavily searches, 3-5 min wall clock).",
            file=sys.stderr,
        )
        return 2
    return asyncio.run(_main(args.idea, args.out))


if __name__ == "__main__":
    raise SystemExit(main())
