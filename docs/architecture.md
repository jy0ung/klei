# Architecture

## Design Principles

Haki is built on four research pillars:

| Pillar | Source | Role |
|--------|--------|------|
| **Brain** | [CognitiveOS](https://cognitive-os.org/) | Dual-tier model orchestration |
| **Memory** | [Honcho](https://docs.honcho.to/) | Persistent learning graph + Theory of Mind |
| **RAG** | [AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/) | Knowledge grounding |
| **Lab** | [Autoresearch](https://github.com/karpathy/autoresearch) | Autonomous model improvement |

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Human)                              │
├─────────────────────────────────────────────────────────────────┤
│                     CLI / TUI (Rich-based)                        │
├─────────────────────────────────────────────────────────────────┤
│                  hakid (daemon — message bus)                     │
├──────────────────┬──────────────────────────────────────────────┤
│  Narrow Model    │  Wide Model (LLM API)                         │
│  (local, fast)   │  (remote, capable)                            │
├──────────────────┴──────────────────────────────────────────────┤
│  Memory Graph  │  RAG Pipeline  │  Lab  │  Self-Healing Health │
├─────────────────────────────────────────────────────────────────┤
│                        MCP Bridges                                │
├─────────────────────────────────────────────────────────────────┤
│                    Host OS (Linux / Win / Mac)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Query Processing

```
User input → CLI
           ↓
      MessageBus.publish("user.input")
           ↓
      Brain.think(query)
           ├── Routes to NARROW (simple queries)
           └── Routes to WIDE (complex reasoning)
           ↓
      Memory.learn_from_interaction(input, output)
           ↓
      BrainResponse → CLI display
```

### 2. Memory Self-Learning Loop

```
Every interaction:
  1. Store raw interaction in SQLite
  2. Extract insights (heuristic or LLM)
  3. Generate embedding via sentence-transformers
  4. Add to FAISS vector index
  5. Update user model (Theory of Mind)
```

### 3. RAG Retrieval Flow

```
Query → Embedding
      ↓
  Memory search (episodic context)
  Document search (static knowledge)
      ↓
  Merge + rank by score
      ↓
  Build augmented prompt
      ↓
  Send to Brain (wide model)
```

### 4. Autoresearch Loop

```
WHILE running:
  1. Generate idea (LLM or heuristic)
  2. Create training data from memory
  3. Fine-tune via LoRA/PEFT (fixed time budget)
  4. Evaluate val_bpb
  5. IF improved → keep model
     ELSE → discard
  6. Log to results.tsv
```

### 5. Health Monitoring

```
Every 30s:
  Check brain (model availability)
  Check memory (DB connectivity)
  Check rag (index integrity)
  Check disk (space)
  Check bus (event flow)
      ↓
  Publish haki.health event
  IF unhealthy → attempt_recovery()
```

## Module Dependencies

```
CLI ──→ Brain ──→ LLM API (remote)
 │              ──→ Local model (optional)
 │
 ├──→ Memory (SQLite + FAISS)
 │       ↑
 ├──→ RAG (builds on Memory)
 │
 ├──→ Lab (fine-tunes using Memory data)
 │
 ├──→ Health (monitors all modules)
 │
 └──→ MessageBus (connects everything)
          ↑
     MCP Bridge (external access)
```

## Storage Layout

```
~/.haki/
├── memory.db              # SQLite: memories, interactions, user_model
├── memory.db.faiss        # FAISS index for memory vectors
├── memory.db.docs.faiss   # FAISS index for RAG documents
├── memory.db.docs.json    # Document text sidecar
├── rag.index              # RAG document cache
├── models/                # Downloaded models (transformers cache)
│   ├── TinyLlama-1.1B-Chat-v1.0/
│   └── sentence-transformers/
├── lab/
│   ├── experiments/       # Experiment configs & checkpoints
│   ├── models/            # Fine-tuned LoRA adapters
│   ├── data/              # Generated training data (JSONL)
│   ├── logs/              # Training logs
│   └── results.tsv        # Experiment results
└── config.json            # (future) runtime config
```

## Threading Model

- **All modules are async** — use `asyncio` via `async/await`
- **MessageBus** is the central coordination primitive (pub/sub)
- **Daemon** runs the event loop, monitoring, and health checks
- **CLI** runs synchronous entry points that bridge into async via `asyncio.run()`

## Configuration

All config via `HakiConfig` (Pydantic Settings):

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_DATA_DIR` | `~/.haki` | Root data directory |
| `HAKI_NARROW_MODEL_ID` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Local model |
| `HAKI_LLM_API_KEY` | `""` | LLM API key |
| `HAKI_LLM_API_BASE` | `https://api.openai.com/v1` | LLM API endpoint |
| `HAKI_LLM_MODEL` | `gpt-4o-mini` | Wide model name |
| `HAKI_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `HAKI_RAG_CHUNK_SIZE` | `512` | RAG chunk size in words |
| `HAKI_RAG_TOP_K` | `5` | RAG retrieval count |
| `HAKI_LAB_TIME_BUDGET` | `300` | Seconds per experiment |
| `HAKI_HEALTH_INTERVAL` | `30` | Health check interval (s) |

## Extending Haki

Add modules by:

1. Create `haki/<module>/__init__.py`
2. Initialize in `daemon/main.py`
3. Subscribe to bus topics
4. Add MCP tools via `mcp/__init__.py`
5. Add CLI commands in `cli/__init__.py`

## Security Notes

- No auth built-in for daemon (localhost only)
- API keys stored in env vars, not persisted
- SQLite DB has no encryption (encrypt at rest separately if needed)
- MCP bridge has no rate limiting (add reverse proxy in prod)
