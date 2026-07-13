# API Reference

**Version:** 0.2.0 — local-only self-evolving brain

## Config

### `haki.config.HakiConfig`

```python
class HakiConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HAKI_", env_file=".env", extra="ignore")

    data_dir: Path
    models_dir: Path
    memory_db: Path
    lab_dir: Path

    base_model_id: str          # default SmolLM2-360M-Instruct
    narrow_model_id: str        # legacy alias of base
    model_load_in_8bit: bool
    model_max_new_tokens: int
    model_cpu: bool

    embedding_model: str
    rag_chunk_size: int
    rag_top_k: int

    lab_time_budget_seconds: int
    lab_gpu: bool
    lab_min_training_pairs: int
    lab_auto_promote: bool

    health_check_interval_seconds: int
    self_heal_interval_seconds: int

    @property
    def active_model_registry(self) -> Path  # lab/active_model.json
```

**Removed:** `llm_api_key`, `llm_api_base`, `llm_model`, remote wide endpoint.

---

## Brain

### `haki.brain.Brain(Organism)`

```python
class Brain(Organism):
    async def initialize() -> None
    async def think(query: str, force_tier=None) -> BrainResponse  # local only
    async def reload() -> bool
    async def promote_adapter(adapter_path, val_bpb=None, base_model=None, description="") -> dict
    def model_card() -> dict
    @property local_loaded -> bool
```

### `BrainResponse`

```python
@dataclass
class BrainResponse:
    text: str
    tier: TierChoice          # always LOCAL
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    adapter: str | None = None
    generation: int = 0
    error: str | None = None
```

---

## Lab

### `haki.lab.Lab(Organism)`

```python
class Lab(Organism):
    async def initialize() -> None
    async def create_training_data_from_memory(allow_seed: bool = True) -> Path
    def training_pair_count(data_path: Path | None = None) -> int
    async def fine_tune_model(..., allow_seed: bool = True) -> ExperimentResult
    async def promote_to_brain(adapter_path, val_bpb=None, base_model=None, description="") -> dict
    async def evolve_once(epochs: int = 1) -> ExperimentResult
    async def evolve_loop(max_experiments: int = 10) -> list[ExperimentResult]
    async def run_autoresearch_loop(max_experiments: int = 100) -> None
    def get_results() -> list[ExperimentResult]
    def get_best_model() -> Path | None
```

---

## Memory / Wiki / RAG / Health / Self-Heal / Kaizen / Daemon

See module docs; public shapes largely as in 0.1.2 with Organism inheritance.

Key entrypoints:

```python
from haki.memory import memory
from haki.wiki import wiki
from haki.rag import rag
from haki.health import monitor
from haki.self_heal import self_healer
from haki.kaizen import kaizen
from haki.daemon.bus import bus, Event
```

---

## CLI

| Command | Description |
|---------|-------------|
| `haki chat` | Local chat |
| `haki brain` | Model card |
| `haki evolve` | Self-evolution cycle(s) |
| `haki lab` | Fine-tune + auto-promote |
| `haki health` / `heal` | Monitor / recover |
| `haki status` | Organism vitality |
| `haki wiki …` | Wiki ops |
| `haki become …` | Tensions / questions |
| `haki kaizen …` | Improvement log |
| `haki daemon` | Background loops |

---

## MCP

| Tool | Notes |
|------|--------|
| `haki_chat` | Local brain only (no force_tier) |
| `haki_remember` / `haki_recall` | Memory |
| `haki_health` | Health JSON |
| `haki_rag_query` | RAG |
| `haki_lab_run` | Fine-tune |
| `wiki_*` | Wiki tools |
