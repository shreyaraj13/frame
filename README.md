# Frame

Multi-agent PM workflow tool. Takes a vague idea and produces a defensible PRD by enforcing structured PM thinking: **problem space discipline** (diverge → converge to one problem statement) before **solution mode** (diverge on solutions → converge via prioritization).

CLI-first. Local-only. Single user.

## Pipeline

```
Idea → Explorer → Synthesizer → [GATE 1] → Ideator → Prioritizer → [GATE 2] → Definer → Critic → PRD
       ─── problem space ───              ─── solution space ───           ─── output ───
```

A **supervisor** Claude conversation orchestrates 6 specialist sub-agents and 2 HITL gates. Killed solutions stay visible in the final PRD as "Alternatives Considered."

## 7 Entry Points

```
[1] Just an idea
[2] Idea + raw evidence
[3] Raw evidence only       → skip to Synthesizer
[4] Locked problem          → skip to Ideator
[5] Locked problem + solution → skip to Definer
[6] Draft PRD               → just Critic
[7] Existing Frame package  → resume / re-run any stage
```

## Quick start

```bash
# install (uses uv)
uv sync

# minimum: API keys + vault path
cp .env.example .env
$EDITOR .env

# run
uv run frame --help
uv run frame start
```

### Optional: clustering for evidence ingestion

`sentence-transformers` + `hdbscan` are heavy installs. Skip until you need to ingest large evidence corpora.

```bash
uv sync --extra embeddings
```

`hdbscan` requires a working C compiler on macOS. If it fails: `xcode-select --install`.

## Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| Package manager | uv |
| LLM | Claude Sonnet 4.6 via `anthropic` |
| Orchestration | Anthropic SDK tool calling (sub-agent as tool) |
| Tool protocol | Inline Python tools for sub-agents; MCP (stdio) for Obsidian |
| CLI | Typer + Rich |
| Schemas | Pydantic v2 |
| Observability | Langfuse (cloud) |
| Evals | DeepEval + pytest |
| Artifacts | Obsidian vault (markdown + YAML frontmatter) |
| Embeddings | sentence-transformers (local) |
| Clustering | HDBSCAN |
| Web search | Tavily |

## Status

**Phase 1: Scaffolding** — done. Skeleton, schemas, stubs, CLI works (`frame --help`).
**Phase 2: Build agents** — Explorer first, then Synthesizer → Gate 1 → Ideator → Prioritizer → Gate 2 → Definer → Critic.
