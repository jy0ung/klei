# API Reference

## Brain

### `haki.brain.Brain`

Dual-tier model orchestrator.

```python
class Brain:
    narrow_model_id: str          # Model identifier
    narrow_model: PreTrainedModel | None
    narrow_tokenizer: PreTrained | None

    async def initialize() → None
    async def think(query: str, force_tier: TierChoice | None = None) → BrainResponse
```

### `BrainResponse`

```python
@dataclass
class BrainResponse:
    text: str                    # Generated response
    tier: TierChoice             # Which tier responded
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str | None = None
```

### `TierChoice`

```python
class TierChoice(str, Enum):
    NARROW = "narrow"    # Local small model
    WIDE = "wide"        # Remote LLM API
```

---

## Memory

### `haki.memory.MemoryGraph`

Persistent, self-learning memory.

```python
class MemoryGraph:
    async def initialize() → None
    async def store_memory(node: MemoryNode) → None
    async def store_interaction(user_input: str, assistant_output: str, tier: str = "") → None
    async def search(query: str, top_k: int | None = None) → list[MemoryNode]
    async def get_all() → list[MemoryNode]
    async def learn_from_interaction(user_input: str, assistant_output: str) → None
    async def update_user_model(theory_of_mind: str, preferences: dict, comm_style: str) → None
    async def get_user_model() → dict[str, Any] | None
    async def get_recent_interactions(n: int = 20) → list[dict]
```

### `MemoryNode`

```python
@dataclass
class MemoryNode:
    id: str
    content: str
    role: str                    # "user", "assistant", "system", "insight"
    embedding: list[float] | None
    metadata: dict[str, Any]
    created_at: datetime
    importance: float
```

---

## RAG

### `haki.rag.RAGPipeline`

Retrieval-augmented generation.

```python
class RAGPipeline:
    async def initialize() → None
    async def add_document(text: str, source: str = "unknown", metadata: dict | None = None) → None
    async def retrieve(query: str, top_k: int | None = None) → RAGResult
    def _chunk_text(text: str, chunk_size: int | None = None, overlap: int = 50) → list[str]
    def _build_augmented_prompt(query: str, chunks: list[dict]) → str
```

### `RAGResult`

```python
@dataclass
class RAGResult:
    query: str
    retrieved_chunks: list[dict[str, Any]]
    augmented_prompt: str
    metadata: dict[str, Any]
```

---

## Lab

### `haki.lab.Lab`

Autonomous model creation.

```python
class Lab:
    async def initialize() → None
    async def create_training_data_from_memory() → Path
    async def fine_tune_model(model_id: str | None = None, epochs: int = 1,
                               time_budget_seconds: int | None = None) → ExperimentResult
    async def run_autoresearch_loop(max_experiments: int = 100) → None
    def get_results() → list[ExperimentResult]
    def get_best_model() → Path | None
    def stop() → None
```

### `ExperimentResult`

```python
@dataclass
class ExperimentResult:
    id: str
    description: str
    status: str                  # "success", "failed", "aborted"
    val_bpb: float | None
    val_loss: float | None
    training_seconds: float
    peak_vram_mb: float
    total_tokens: int
    description_text: str
    created_at: datetime
```

---

## Health

### `haki.health.HealthMonitor`

Self-healing subsystem.

```python
class HealthMonitor:
    async def run() → None                    # Continuous monitoring loop
    async def check_all() → SystemHealth
    def get_report() → SystemHealth
    def register_check(name: str, callback: Callable) → None
    async def attempt_recovery(component: str) → bool
    def stop() → None
```

### `SystemHealth`

```python
@dataclass
class SystemHealth:
    overall: ComponentStatus
    checks: list[HealthCheck]
    uptime_seconds: float
    memory_usage_mb: float
```

### `ComponentStatus`

```python
class ComponentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
```

---

## Daemon / MessageBus

### `haki.daemon.bus.MessageBus`

```python
class MessageBus:
    def subscribe(topic: str, callback: Callable) → None
    def unsubscribe(topic: str, callback: Callable) → None
    async def publish(event: Event) → None
    def publish_sync(event: Event) → None
    def recent(topic: str | None = None, n: int = 50) → list[Event]
```

### `Event`

```python
@dataclass
class Event:
    topic: str
    payload: Any
    timestamp: datetime
    source: str
```

### Bus Topics

| Topic | Payload | Source |
|-------|---------|--------|
| `haki.start` | `{}` | daemon |
| `haki.ready` | `{}` | daemon |
| `haki.stop` | `{}` | daemon |
| `haki.health` | `SystemHealth.to_dict()` | health |
| `haki.shutdown` | `{}` | user |

---

## MCP Bridge

### `haki.mcp.MCPBridge`

```python
class MCPBridge:
    TOOLS: list[dict]             # MCP tool definitions

    async def list_tools() → list[dict]
    async def call_tool(name: str, arguments: dict) → list[dict]
```

### Available Tools

| Tool | Description |
|------|-------------|
| `haki_chat` | Send message to brain |
| `haki_remember` | Store persistent memory |
| `haki_recall` | Semantic memory search |
| `haki_health` | System health status |
| `haki_rag_query` | RAG-augmented query |
| `haki_lab_run` | Run model creation experiment |

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `haki init` | Initialize directories |
| `haki daemon` | Start daemon |
| `haki chat [-m msg] [--tier]` | Chat or single message |
| `haki health` | Health report |
| `haki lab [--model] [--epochs]` | Run fine-tuning |
| `haki rag <query>` | RAG query |
| `haki ingest <file>` | Add document |
| `haki status` | Quick status |
