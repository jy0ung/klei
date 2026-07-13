"""Haki — Cognitive OS config (local-first, no cloud LLM required)."""
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

    # Local brain only — tiny base that fits ~4GB machines
    # SmolLM2-360M is small enough for CPU/low-RAM; Lab evolves LoRA adapters on top.
    base_model_id: str = Field(default="HuggingFaceTB/SmolLM2-360M-Instruct")
    # Legacy alias used by older docs/tests
    narrow_model_id: str = Field(default="HuggingFaceTB/SmolLM2-360M-Instruct")

    # Quantization / device (4GB-friendly defaults)
    model_load_in_8bit: bool = Field(default=False)
    model_max_new_tokens: int = Field(default=128)
    model_cpu: bool = Field(default=True)  # prefer CPU unless GPU explicitly enabled

    # RAG
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    rag_chunk_size: int = Field(default=512)
    rag_top_k: int = Field(default=5)

    # Lab / self-evolution
    lab_time_budget_seconds: int = Field(default=300)
    lab_gpu: bool = Field(default=False)  # 4GB default: CPU-friendly
    lab_min_training_pairs: int = Field(default=3)
    lab_auto_promote: bool = Field(default=True)  # replace active brain when improved

    # Health
    health_check_interval_seconds: int = Field(default=30)
    self_heal_interval_seconds: int = Field(default=300)

    @property
    def active_model_registry(self) -> Path:
        return self.lab_dir / "active_model.json"


config = HakiConfig()

# Keep narrow_model_id in sync with base if only one is set via env
if config.narrow_model_id != config.base_model_id:
    # Prefer explicit base_model_id when both differ and base is default-overridden
    pass
