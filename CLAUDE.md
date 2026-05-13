# Frame — Claude Code project memory

## What this is
Multi-agent PM workflow tool. Vague idea → defensible PRD by forcing problem-space discipline (diverge → converge → GATE) before solution mode (diverge → converge → GATE) before output (Definer + Critic).

## Architecture (locked)
- **Supervisor**: one Claude conversation with phase-enforcement system prompt. Drives the pipeline. State = a Pydantic `FrameState` passed between turns.
- **6 sub-agents as tools**: Explorer, Synthesizer, Ideator, Prioritizer, Definer, Critic. Each is a Claude conversation underneath, exposed to the supervisor as one tool. Tools live in `frame/subagents/*.py`. **In-process Python — NOT separate MCP servers** (decision below).
- **2 HITL gates as tools**: `present_gate_to_user()` blocks on Rich prompt. Implementation in `frame/tools/gates.py`.
- **Obsidian writes**: real MCP server at `mcp_servers/obsidian_mcp/server.py` — the only true MCP server in the project. Reusable from Claude Desktop too.
- **State**: Pydantic models in `frame/schemas/`. `FrameState` is the top-level. Serialize to `.frame_state.json` for resume.

## Why inline sub-agents, MCP only for Obsidian
- 7 stdio MCP servers for an internal Python CLI = 7 subprocesses, 7 JSON-RPC round trips, harder to trace. No external client reuses these tools.
- Obsidian is the exception: a markdown-vault writer is genuinely useful from Claude Desktop, Cursor, etc. → worth shipping as a real MCP server (also a portfolio signal).
- If we later want a sub-agent reusable across clients, promote it to an MCP server then. Don't speculatively build them.

## Build order (Phase 2)
1. **Explorer** — most complex, sets the sub-agent pattern. Includes evidence ingestion path.
2. **Synthesizer** — closes problem space. First gate uses its output.
3. **Gate 1** wiring + supervisor phase enforcement.
4. **Ideator** — solution divergence.
5. **Prioritizer** — solution convergence. Killed-solutions appendix structure decided here.
6. **Gate 2** wiring.
7. **Definer** — PRD generation. Pulls locked problem + locked solution + killed solutions.
8. **Critic** — final pass.
9. **Evidence ingestion + clustering** — wire HDBSCAN path. Defer until Explorer's stub clearly needs it.
10. **Obsidian MCP** — package writes, decision log, vault reads (entry point 7).
11. **Langfuse** — wrap every Claude call + tool call. Trace IDs in vault frontmatter.
12. **Evals** — 15 golden ideas, DeepEval rubrics, pytest pipeline.

## Conventions
- **Model**: always `claude-sonnet-4-6`. Don't hardcode — read from `frame.config.settings.model`.
- **Schemas first**: every sub-agent's input/output is a Pydantic model. Tool result = `model.model_dump_json()`. Tool input = parsed via `Model.model_validate_json()`.
- **Sub-agent contract**: `async def run(state: FrameState, **inputs) -> SomeResult`. Stateless from the supervisor's POV — supervisor passes whatever the sub-agent needs.
- **No agent-to-agent calls**: only the supervisor calls sub-agents. Sub-agents return data; they don't trigger other sub-agents.
- **HITL gates are tools**: the supervisor decides when to call a gate. The gate blocks until the user picks.
- **Killed solutions persist**: every entry in `state.killed_solutions` carries `reason_killed`. Definer reads this list to write the "Alternatives Considered" appendix.
- **Evidence is first-class**: every problem/solution carries `supporting_evidence_ids` linking back to `EvidenceCorpus.items[i].id`. Don't lose traceability.

## Gear discipline (from global CLAUDE.md)
- **SCOPE EXPAND** (vision): only when the user is brainstorming. Never during a build session.
- **SCOPE HOLD** (build): default. Only build what was asked. No speculative abstractions.
- **SCOPE REDUCE** (cut): when an agent grows past its prompt budget or its job blurs into another agent's.

## What's done
- Full file tree, Pydantic schemas, stubbed supervisor + sub-agents, prompt skeleton files, obsidian MCP template, CLI works (`frame --help`).
- No real LLM calls yet. No real tool implementations.

## What's next
Start Phase 2 step 1: Explorer. Read `frame/prompts/explorer.md`, build `frame/subagents/explorer.py`, write Tavily search tool, write `tests/test_subagents.py::test_explorer_smoke`. One agent per session.

## Decisions log
Append to this file when an architectural decision is made. Keep one-liners; details in PR/commit.

- 2026-05-13: Inline Python sub-agents; Obsidian as the only real MCP server.
- 2026-05-13: Sentence-transformers + HDBSCAN for evidence dedup; sampling fallback when clustering degenerate.
- 2026-05-13: Langfuse cloud free tier (not self-hosted).
- 2026-05-13: Fresh `~/Obsidian/Frame` vault — Frame owns it.
- 2026-05-13: Python pinned to 3.12 via `.python-version`. Reason: Python 3.13 + uv on macOS silently breaks editable installs (uv hides `.venv`, Python 3.13's `site.py` now skips hidden .pth files). Symptom: `uv run frame` → `ModuleNotFoundError: No module named 'frame'` despite a clean `uv sync`. Workaround if forced to 3.13: `find .venv -name '*.pth' -exec chflags nohidden {} +` after every sync.
- 2026-05-14: Pinning Python 3.12 alone is NOT enough — the UF_HIDDEN check was backported into Homebrew's 3.12.13 (and possibly other 3.12.x). Real fix: a `Makefile` that wraps `uv sync` and chflags-unhides .pth files. Always use `make sync` / `make test` / `make run ARGS="..."` instead of raw `uv` commands. Tests work via plain `uv run pytest` (pytest collects from cwd which is in sys.path), but the installed `frame` console script needs the unhide.
- 2026-05-14: Phase 2 step 1 (Explorer) complete. Inline Python tool delivery confirmed: `mcp_servers/explorer_mcp/tools.py` is the single source of truth (Anthropic schemas + impls); `frame/subagents/explorer.py` dispatches inline; `mcp_servers/explorer_mcp/server.py` wraps the same impls as a runnable MCP server for external reuse. `submit_exploration` runs in strict mode (Pydantic ValidationError propagates; no retry).
