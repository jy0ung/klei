"""Haki — Cognitive OS core exceptions and config."""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HakiConfig(BaseSettings):
    """Global configuration loaded from environment or .env."""

    model_config = SettingsConfigDict(
        env_prefix="HAKI_",
        env_file=".env",
        extra="ignore",
    )

    # Paths
    data_dir: Path = Field(default=Path.home() / ".haki")
    models_dir: Path = Field(default=Path.home() / ".haki" / "models")
    memory_db: Path = Field(default=Path.home() / ".haki" / "memory.db")
    rag_index: Path = Field(default=Path.home() / ".haki" / "rag.index")
    lab_dir: Path = Field(default=Path.home() / ".haki" / "lab")

    # Models
    narrow_model_id: str = Field(default="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    wide_model_endpoint: str = Field(default="http://localhost:8000/v1")

    # LLM API
    llm_api_key: str = Field(default="")
    llm_api_base: str = Field(default="https://api.openai.com/v1")
    llm_model: str = Field(default="gpt-4o-mini")

    # RAG
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    rag_chunk_size: int = Field(default=512)
    rag_top_k: int = Field(default=5)

    # Lab
    lab_time_budget_seconds: int = Field(default=300)
    lab_gpu: bool = Field(default=True)
    lab_min_training_pairs: int = Field(default=3)

    # Health
    health_check_interval_seconds: int = Field(default=30)
    self_heal_interval_seconds: int = Field(default=300)


config = HakiConfig()
