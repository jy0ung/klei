# Architecture

**Version:** 0.1.2

## Design Principles

1. **Intent-centric** — human sets goals; Haki operates modules  
2. **Becoming, not being** — modules are living organisms with lifecycle + metabolism  
3. **Compounding knowledge** — Wiki compiles sources; Memory captures interactions  
4. **Kaizen** — small permanent fixes, measured and logged  
5. **Low-risk self-heal** — recover without destructive side effects  

## Research Pillars

| Pillar | Source | Role |
|--------|--------|------|
| **Brain** | [CognitiveOS](https://cognitive-os.org/) | Dual-tier orchestration |
| **Memory** | [Honcho](https://docs.honcho.to/) | Graph + Theory of Mind |
| **Wiki** | [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | Persistent markdown knowledge |
| **RAG** | [AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/) | Retrieval grounding |
| **Lab** | [Autoresearch](https://github.com/karpathy/autoresearch) | Experiment / fine-tune loop |
| **Self-Heal** | Self-healing agent patterns | L2 recovery cycles |

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Human)                              │
├─────────────────────────────────────────────────────────────────┤
│              CLI (Rich) · MCP tools · status / heal              │
├─────────────────────────────────────────────────────────────────┤
│   hakid — MessageBus + Health + Becoming + SelfHealer            │
├──────────────────┬──────────────────────────────────────────────┤
│  Narrow Model    │  Wide Model (LLM API)                         │
├──────────────────┴──────────────────────────────────────────────┤
│ Memory │ Wiki │ RAG │ Lab │ Health │ Kaizen │ Philosophy         │
├─────────────────────────────────────────────────────────────────┤
│                    Host OS (Linux / Win / Mac)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Living Modules (Organisms)

| Module | Class | Notes |
|--------|-------|-------|
| Brain | `Brain(Organism)` | Routes + pulses on think |
| Memory | `MemoryGraph(Organism)` | Insights + user model |
| Wiki | `Wiki(Organism)` | Markdown graph |
| Lab | `Lab(Organism)` | Fine-tune + seed data |
| Health | `HealthMonitor(Organism)` | Checks + recovery |
| Daemon | `HakiDaemon(Organism)` | Orchestrates loops |
| Self-Heal | `SelfHealer(Organism)` | Autonomous recovery |

## Data Flow

### 1. Query Processing

```
User → CLI chat
     → Brain.think(query)   # narrow | wide
     → Memory.learn_from_interaction()
     → insights + user_model update
     → response panel
```

### 2. Memory Self-Learning

```
interaction
  → store in SQLite
  → multi-pattern insight extraction
  → embeddings (sentence-transformers)
  → FAISS index
  → Theory of Mind user_model row
```

### 3. Wiki Knowledge Compile

```
source ingest
  → sources/ page
  → entities/ + concepts/
  → index.md + log.md
  → content-aware query (title×3 + tags×2 + content×1)
```

### 4. RAG

```
query → memory vectors + doc index → top_k → augmented prompt
```

### 5. Lab / Autoresearch

```
interactions (or seed pairs)
  → training.jsonl
  → LoRA fine-tune (after min pair gate)
  → val_bpb approximation
  → results.tsv + best adapter path
```

### 6. Health + Self-Heal

```
every health_interval:
  check brain/memory/rag/wiki/disk/bus
  publish haki.health

every self_heal_interval (or haki heal):
  for degraded/unhealthy components:
    low-risk recover (re-init; no heavy model downloads)
  publish haki.self_heal
  record kaizen if recoveries succeeded
```

### 7. Becoming

```
every 5 minutes:
  gather module stats
  scan tensions (gap, stasis, novelty, contradiction)
  generate questions
  propose transformation
  publish haki.becoming
```

## Storage Layout

```
~/.haki/
├── memory.db (+ .faiss)
├── wiki/                 # schema, index, log, entities, concepts, ...
├── lab/
│   ├── data/training.jsonl
│   ├── models/<exp_id>/adapter/
│   └── results.tsv
├── models/               # HF cache
└── kaizen.jsonl          # continuous improvement log
```

## Configuration

Via `HakiConfig` (`pydantic-settings`, `SettingsConfigDict`, env prefix `HAKI_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `~/.haki` | Root |
| `NARROW_MODEL_ID` | TinyLlama 1.1B | Local model |
| `LLM_API_KEY` | `""` | Wide API key |
| `LLM_API_BASE` | OpenAI | Endpoint |
| `LLM_MODEL` | `gpt-4o-mini` | Wide model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embeddings |
| `RAG_CHUNK_SIZE` | `512` | Words/chunk |
| `RAG_TOP_K` | `5` | Retrieve count |
| `LAB_TIME_BUDGET` | `300` | Seconds |
| `LAB_MIN_TRAINING_PAIRS` | `3` | Min pairs |
| `HEALTH_INTERVAL` | `30` | Seconds |
| `SELF_HEAL_INTERVAL` | `300` | Seconds |

## Bus Topics

| Topic | Purpose |
|-------|---------|
| `haki.start` / `ready` / `stop` / `shutdown` | Lifecycle |
| `haki.health` | Health report payload |
| `haki.becoming` | Tensions + proposals |
| `haki.self_heal` | Recovery actions |

## Module Dependencies

```
CLI → Brain, Memory, Wiki, RAG, Lab, Health, SelfHealer, Kaizen
Daemon → HealthMonitor, Becoming, SelfHealer, MessageBus
Lab → Memory (training pairs)
RAG → Memory + FAISS docs
Wiki → filesystem markdown
Brain → optional local HF model + remote LLM API
```

## Extending

1. Subclass `Organism` when possible  
2. `async def initialize()` + `pulse()` on real work  
3. Register health checks / self-heal recoverers  
4. Add CLI + MCP tools  
5. Document in `docs/modules/`  
6. Record improvement with `haki kaizen add`  

## Security Notes

- Daemon is localhost-oriented; no built-in multi-tenant auth  
- Self-heal never auto-downloads large models  
- API keys only via env / `.env`  
- SQLite not encrypted at rest  
