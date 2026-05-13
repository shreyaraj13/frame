"""Frame runtime config — loaded from .env via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: str = ""
    model: str = Field(default="claude-sonnet-4-6", alias="FRAME_MODEL")
    max_tokens: int = Field(default=8000, alias="FRAME_MAX_TOKENS")

    obsidian_vault_path: Path = Path.home() / "Obsidian" / "Frame"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    tavily_api_key: str = ""

    log_level: str = Field(default="INFO", alias="FRAME_LOG_LEVEL")
    embeddings_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="FRAME_EMBEDDINGS_MODEL",
    )

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
