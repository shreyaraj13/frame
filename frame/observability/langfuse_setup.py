"""Initialize the Langfuse client. Returns None if keys aren't configured."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from frame.config import get_settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_langfuse() -> Any | None:
    s = get_settings()
    if not s.langfuse_enabled:
        log.info("Langfuse not configured — tracing disabled")
        return None
    try:
        from langfuse import Langfuse
    except ImportError:
        log.warning("langfuse not installed")
        return None
    return Langfuse(
        public_key=s.langfuse_public_key,
        secret_key=s.langfuse_secret_key,
        host=s.langfuse_host,
    )
