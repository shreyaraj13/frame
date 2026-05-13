"""Decorators / context managers that wrap sub-agent + tool calls in a trace.

Phase 1: pass-through. Phase 2: real spans with input/output/cost capture.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from frame.observability.langfuse_setup import get_langfuse


@contextmanager
def trace_span(name: str, **metadata: Any):
    """Create a span if Langfuse is configured, else no-op."""
    lf = get_langfuse()
    if lf is None:
        yield None
        return
    # Phase 2: lf.span(name=name, metadata=metadata) etc.
    yield None
