.PHONY: sync test run unhide

# Workaround: uv hides every file in .venv on macOS via UF_HIDDEN, and recent
# CPython (3.12.13+, 3.13.x) silently skips hidden .pth files in site.py,
# which breaks editable installs. After every sync, unhide the .pth files.
unhide:
	@find .venv -name "*.pth" -exec chflags nohidden {} + 2>/dev/null || true

sync:
	uv sync
	@$(MAKE) unhide

sync-dev:
	uv sync --extra dev
	@$(MAKE) unhide

test: unhide
	uv run pytest -q

# Overrides the default `-m 'not integration'` addopts in pyproject.toml.
test-integration: unhide
	uv run pytest -q -m integration --override-ini="addopts="

run: unhide
	uv run frame $(ARGS)

# Run Explorer against a single idea. Real $$ — requires CONFIRM=yes.
# Cost: ~$0.20-0.40 Claude + ~6 Tavily searches + 3-5 min wall clock.
explore: unhide
	@if [ -z "$(IDEA)" ]; then echo "Missing IDEA. Usage: make explore IDEA=\"your idea\" CONFIRM=yes"; exit 1; fi
	@if [ "$(CONFIRM)" != "yes" ]; then echo "Cost: ~\$$0.30 + Tavily searches. Re-run with: make explore IDEA=\"$(IDEA)\" CONFIRM=yes"; exit 1; fi
	uv run python bin/run_explorer.py "$(IDEA)" --confirm $(if $(OUT),--out $(OUT))
