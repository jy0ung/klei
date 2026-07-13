# Architecture

**Version:** 0.2.0 — local-only self-evolving brain

## Design Principles

1. **Local-only inference** — no cloud LLM API for the product brain  
2. **Self-replacement** — Lab promotes better adapters into the living brain  
3. **Becoming, not being** — modules are organisms with lifecycle + metabolism  
4. **Compounding knowledge** — Wiki compiles; Memory captures; Lab specializes  
5. **Kaizen** — small permanent fixes, measured and logged  
6. **Low-risk self-heal** — recover without surprise model downloads  

## Research Pillars

| Pillar | Source | Role in Haki |
|--------|--------|----------------|
| **Brain** | CognitiveOS (intent layer) | Local tiny model + LoRA generations |
| **Memory** | Honcho | Graph + Theory of Mind |
| **Wiki** | Karpathy LLM Wiki | Compiled markdown knowledge |
| **RAG** | AWS RAG pattern | Retrieval grounding |
| **Lab** | Karpathy Autoresearch | Fixed-budget train → val_bpb → keep/promote |
| **Self-Heal** | Self-healing agents | L2 recovery |
| **Kaizen** | Continuous improvement | Defect/waste log |

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Human)                              │
├─────────────────────────────────────────────────────────────────┤
│     CLI (Rich) · MCP · brain / evolve / heal / kaizen            │
├─────────────────────────────────────────────────────────────────┤
│   hakid — MessageBus + Health + Becoming + SelfHealer            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   LOCAL BRAIN (generation N)                                     │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │  Base: SmolLM2-360M-Instruct (or HAKI_BASE_MODEL_ID)     │   │
│   │  + optional LoRA from ~/.haki/lab/active_model.json      │   │
│   │  Rule fallback if weights not loaded                     │   │
│   └──────────────────────────────────────────────────────────┘   │
│                         ▲ promote if better val_bpb              │
│                         │                                        │
│   LAB (Autoresearch-style)                                       │
│   train LoRA on memory/seed → evaluate val_bpb → keep/discard    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Memory │ Wiki │ RAG │ Health │ Kaizen │ Philosophy               │
├─────────────────────────────────────────────────────────────────┤
│                    Host OS (Linux / Win / Mac)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Self-evolution (core product loop)

```
1. User chats → SpecializedBrain.think (assess/research/experiment/learn)
2. Mastery map updated; memory/wiki evidence compounds
3. haki evolve / Lab.evolve_once when self-improve experiment runs
4. LoRA fine-tune on base model
5. If best → promote → generation N+1
```

### Specialized brain (v0.3)

Control is **code**, not cloud LLM:

- **Assess** mastery confidence  
- **Research** memory + wiki + RAG if unknown  
- **Experiment** hypothesis store or Lab evolve for self-topics  
- **Synthesize** structural (+ optional local neural polish)  
- **Learn** mastery + memory  

See [modules/cognition.md](modules/cognition.md).

### active_model.json

```json
{
  "base_model": "HuggingFaceTB/SmolLM2-360M-Instruct",
  "adapter_path": "C:/Users/.../.haki/lab/models/<id>/adapter",
  "val_bpb": 0.99,
  "generation": 3,
  "description": "increase LoRA rank..."
}
```

Path: `~/.haki/lab/active_model.json` (`config.active_model_registry`).

## Living Modules (Organisms)

| Module | Class | Notes |
|--------|-------|-------|
| Brain | `Brain(Organism)` | Local generate + promote/reload |
| Memory | `MemoryGraph(Organism)` | Insights + user model |
| Wiki | `Wiki(Organism)` | Markdown graph |
| Lab | `Lab(Organism)` | Evolve + auto-promote |
| Health | `HealthMonitor(Organism)` | Checks + recovery |
| Daemon | `HakiDaemon(Organism)` | Orchestrates loops |
| Self-Heal | `SelfHealer(Organism)` | Autonomous recovery |

## Data Flow

### 1. Query (local)

```
User → CLI chat
     → Brain.think(query)     # local model or rule fallback
     → Memory.learn_from_interaction()
     → insights + user_model
     → response (shows generation N)
```

### 2. Memory self-learning

```
interaction → SQLite
           → multi-pattern insights
           → embeddings + FAISS
           → user_model (Theory of Mind)
```

### 3. Wiki compile

```
ingest → sources/entities/concepts
      → index.md + log.md
      → content-aware query
```

### 4. RAG

```
query → memory + doc vectors → top_k → augmented prompt
      → (optionally) Brain.think
```

### 5. Lab / Autoresearch

```
memory (+ seed pairs if allow_seed)
  → training.jsonl
  → LoRA fine-tune (fail-fast if empty)
  → val_bpb
  → if NEW BEST and lab_auto_promote → brain.promote_adapter
  → results.tsv
```

### 6. Health + Self-Heal

```
every health_interval: check brain/memory/rag/wiki/disk/bus
every self_heal_interval (or haki heal):
  low-risk recover (re-init; no surprise downloads)
```

### 7. Becoming

```
every ~5m: scan tensions → questions → propose transformation
publish haki.becoming
```

## Storage Layout

```
~/.haki/
├── memory.db (+ .faiss)
├── wiki/
├── models/                      # HF cache for base model
├── lab/
│   ├── active_model.json        # living brain pointer
│   ├── data/training.jsonl
│   ├── models/<exp_id>/adapter/ # LoRA generations
│   ├── results.tsv
│   └── logs/
└── kaizen.jsonl
```

## Configuration

`HakiConfig` — env prefix `HAKI_`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_MODEL_ID` | SmolLM2-360M-Instruct | Local base |
| `NARROW_MODEL_ID` | same | Legacy alias |
| `MODEL_CPU` | `true` | Prefer CPU |
| `MODEL_MAX_NEW_TOKENS` | `128` | Generation length |
| `MODEL_LOAD_IN_8BIT` | `false` | 8-bit if GPU |
| `LAB_GPU` | `false` | CUDA for Lab |
| `LAB_AUTO_PROMOTE` | `true` | Self-replace on best |
| `LAB_MIN_TRAINING_PAIRS` | `3` | Gate before train |
| `LAB_TIME_BUDGET` | `300` | Seconds |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embeddings |
| `HEALTH_INTERVAL` | `30` | Seconds |
| `SELF_HEAL_INTERVAL` | `300` | Seconds |

**Removed (v0.2.0):** `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`, dual-tier wide model.

## Bus Topics

| Topic | Purpose |
|-------|---------|
| `haki.start` / `ready` / `stop` / `shutdown` | Lifecycle |
| `haki.health` | Health payload |
| `haki.becoming` | Tensions + proposals |
| `haki.self_heal` | Recovery actions |

## Module Dependencies

```
CLI → Brain, Lab, Memory, Wiki, RAG, Health, SelfHealer, Kaizen
Lab → Memory (data) → Brain.promote_adapter (self-replace)
Brain → base weights + optional LoRA from Lab
Daemon → Health + Becoming + SelfHealer + Bus
```

## Hardware notes

| Machine | Guidance |
|---------|----------|
| 4GB RAM | SmolLM2-360M, `MODEL_CPU=true`, small `MAX_NEW_TOKENS` |
| 8GB+ | Same; more headroom for Lab |
| GPU | `HAKI_LAB_GPU=true`, optional 8-bit |

## What Haki is not

- Not a replacement for Hermes daily agent workflows  
- Not a cloud multi-model gateway  
- Not full Karpathy `train.py` mutation Autoresearch (yet) — LoRA evolve + promote is the v0.2 path  

## Related docs

- [modules/brain.md](modules/brain.md)  
- [modules/lab.md](modules/lab.md)  
- [philosophy.md](philosophy.md)  
- [quickstart.md](quickstart.md)  
