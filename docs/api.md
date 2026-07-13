# API Reference

**Version:** 0.1.2

## Config

### `haki.config.HakiConfig`

```python
class HakiConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HAKI_", env_file=".env", extra="ignore")

    data_dir: Path
    models_dir: Path
    memory_db: Path
    lab_dir: Path
    narrow_model_id: str
    llm_api_key: str
    llm_api_base: str
    llm_model: str
    embedding_model: str
    rag_chunk_size: int
    rag_top_k: int
    lab_time_budget_seconds: int
    lab_gpu: bool
    lab_min_training_pairs: int
    health_check_interval_seconds: int
    self_heal_interval_seconds: int
```

Singleton: `from haki.config import config`

---

## Organism

### `haki.organism.Organism`

Base class for living modules.

```python
class Organism:
    name: str
    stage: LifeStage
    metabolism: Metabolism

    def pulse(operation: str = "", input_bytes: int = 0, output_bytes: int = 0) -> None
    def error() -> None
    def adapt(reason: str, change: dict) -> None
    def transform(new_structure: dict) -> None
    def get_vitality() -> dict
    def die() -> None
    @property is_alive -> bool
```

`LifeStage`: `birth | growth | maturity | transformation | dormancy | death`

---

## Brain

### `haki.brain.Brain(Organism)`

```python
class Brain(Organism):
    async def initialize() -> None
    async def think(query: str, force_tier: TierChoice | None = None) -> BrainResponse
    def route_stats() -> dict[str, int]   # if present
    @property narrow_loaded -> bool
    @property wide_configured -> bool
```

### `BrainResponse` / `TierChoice`

```python
@dataclass
class BrainResponse:
    text: str
    tier: TierChoice
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str | None = None

class TierChoice(str, Enum):
    NARROW = "narrow"
    WIDE = "wide"
```

---

## Memory

### `haki.memory.MemoryGraph(Organism)`

```python
class MemoryGraph(Organism):
    async def initialize() -> None
    async def store_memory(node: MemoryNode) -> None
    async def store_interaction(user_input: str, assistant_output: str, tier: str = "") -> None
    async def search(query: str, top_k: int | None = None) -> list[MemoryNode]
    async def get_all() -> list[MemoryNode]
    async def learn_from_interaction(user_input: str, assistant_output: str) -> None
    async def update_user_model(theory_of_mind: str, preferences: dict, comm_style: str) -> None
    async def get_user_model() -> dict | None
    async def get_recent_interactions(n: int = 20) -> list[dict]
```

Insight extraction covers preferences, dislikes, name, goals, constraints, workplace, style.

---

## Wiki

### `haki.wiki.Wiki(Organism)`

```python
class Wiki(Organism):
    async def initialize() -> None
    async def ingest_source(path, title=None, summary=None, entities=None, concepts=None) -> dict
    async def ingest_text(title, text, source="memory", entities=None, concepts=None) -> dict
    async def query(question, top_k=5) -> dict   # content-aware scoring
    async def lint() -> WikiLintResult
    async def get_all_pages() -> list[WikiPage]
    def wiki_path() -> Path
```

---

## RAG

### `haki.rag.RAGPipeline`

```python
class RAGPipeline:
    async def initialize() -> None
    async def add_document(text: str, source: str = "unknown", metadata: dict | None = None) -> None
    async def retrieve(query: str, top_k: int | None = None) -> RAGResult
```

---

## Lab

### `haki.lab.Lab(Organism)`

```python
class Lab(Organism):
    async def initialize() -> None
    async def create_training_data_from_memory(allow_seed: bool = True) -> Path
    def training_pair_count(data_path: Path | None = None) -> int
    async def fine_tune_model(
        model_id: str | None = None,
        epochs: int = 1,
        time_budget_seconds: int | None = None,
        allow_seed: bool = True,
    ) -> ExperimentResult
    async def run_autoresearch_loop(max_experiments: int = 100) -> None
    def get_results() -> list[ExperimentResult]
    def get_best_model() -> Path | None
    def stop() -> None
```

Seeds baseline instruction pairs when history is below `lab_min_training_pairs`.

---

## Health

### `haki.health.HealthMonitor(Organism)`

```python
class HealthMonitor(Organism):
    async def run() -> None
    async def check_all() -> SystemHealth
    def get_report() -> SystemHealth
    def register_check(name: str, callback: Callable) -> None
    async def attempt_recovery(component: str) -> bool
    def stop() -> None
```

Checks: `brain`, `memory`, `rag`, `wiki`, `disk`, `bus`.

---

## Self-Heal

### `haki.self_heal.SelfHealer(Organism)`

```python
class SelfHealer(Organism):
    async def cycle() -> dict
    async def recover(component: str, message: str = "") -> HealAction
    def history(n: int = 20) -> list[dict]
```

Low-risk recovery only (re-init modules; no large model downloads).

---

## Kaizen

### `haki.kaizen.KaizenLog`

```python
class KaizenLog:
    def record(title, problem, action, impact, category="general", status="done") -> Improvement
    def list(limit: int = 50) -> list[Improvement]
    def stats() -> dict
```

`seed_if_empty()` records bootstrap improvements once.

---

## Philosophy / Becoming

### `haki.philosophy.Becoming`

```python
class Becoming:
    async def scan_for_tensions(context: dict) -> list[Tension]
    async def generate_question(tension: Tension | None = None) -> Question
    async def propose_transformation(tensions: list[Tension]) -> dict
```

---

## Daemon / Bus

### `MessageBus`

```python
class MessageBus:
    def subscribe(topic: str, callback: Callable) -> None
    def unsubscribe(topic: str, callback: Callable) -> None
    async def publish(event: Event) -> None
    def publish_sync(event: Event) -> None
    def recent(topic: str | None = None, n: int = 50) -> list[Event]
```

### `HakiDaemon(Organism)`

Runs health, becoming, and self-heal loops.

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `haki_chat` | Brain chat |
| `haki_remember` / `haki_recall` | Memory write/search |
| `haki_health` | Health report |
| `haki_rag_query` | RAG retrieve |
| `haki_lab_run` | Fine-tune experiment |
| `wiki_init` / `wiki_ingest` / `wiki_query` / `wiki_lint` | Wiki ops |

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `haki init` | Create data dirs |
| `haki daemon` | Start daemon |
| `haki chat [-m] [--tier]` | Chat |
| `haki health` | Health report |
| `haki heal` | One self-heal cycle |
| `haki status` | Organism vitality |
| `haki lab [--model] [--epochs]` | Fine-tune |
| `haki rag <query>` | RAG query |
| `haki ingest <file>` | Ingest into RAG |
| `haki wiki …` | Wiki init/ingest/query/lint/status |
| `haki become …` | status/question/propose |
| `haki kaizen …` | list/add/stats |
