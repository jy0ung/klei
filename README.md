# Haki — Cognitive OS

> A cognitive OS with brain, self-learning, self-healing, continuous improvement (Kaizen), and the ability to create its own specialized AI model.

**Version:** 0.1.2 · **License:** MIT

Haki integrates research pillars into a single autonomous system that **becomes** rather than merely **runs**:

| Pillar | Source | Role |
|--------|--------|------|
| **Brain** | [CognitiveOS](https://cognitive-os.org/) | Dual-tier model orchestration (narrow local + wide remote) |
| **Memory** | [Honcho](https://docs.honcho.to/) | Persistent memory graph + Theory of Mind |
| **Wiki** | [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | LLM-maintained compounding knowledge base |
| **RAG** | [AWS RAG](https://aws.amazon.com/what-is/retrieval-augmented-generation/) | Retrieval-augmented generation |
| **Lab** | [Autoresearch](https://github.com/karpathy/autoresearch) | Fixed-budget experiment loop / LoRA fine-tuning |
| **Becoming** | Living-system design | Self-questioning tensions → transformations |
| **Kaizen** | Continuous improvement | Defect/waste log that compounds fixes |
| **Self-Heal** | Self-healing agents | L2 recovery cycle for degraded modules |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User (Human)                        │
├─────────────────────────────────────────────────────────┤
│              CLI (Rich) · MCP Bridge · TUI               │
├─────────────────────────────────────────────────────────┤
│     hakid daemon — bus + health + becoming + self-heal   │
├──────────────────┬──────────────────────────────────────┤
│  Narrow Model    │  Wide Model (LLM API)                 │
│  (local, fast)   │  (remote, capable)                    │
├──────────────────┴──────────────────────────────────────┤
│ Memory │ Wiki │ RAG │ Lab │ Health │ Kaizen │ Self-Heal │
├─────────────────────────────────────────────────────────┤
│                      Host OS                             │
└─────────────────────────────────────────────────────────┘
```

Every core module is an **Organism** with lifecycle + metabolism. See [docs/philosophy.md](docs/philosophy.md).

## Quick Start

```bash
# Install
pip install -e .

# Initialize data dirs
haki init

# Chat
haki chat

# Health + self-heal
haki health
haki heal

# Continuous improvement
haki kaizen list
haki kaizen stats

# Wiki
haki wiki init
haki wiki ingest report.md --entities "Python" --concepts "AI"

# Lab (seeds baseline pairs if chat history is thin)
haki lab

# Daemon (health + becoming + self-heal loops)
haki daemon
```

## Modules

| Path | Role |
|------|------|
| `haki/brain/` | Dual-tier orchestration (`Brain(Organism)`) |
| `haki/memory/` | SQLite + FAISS memory graph |
| `haki/wiki.py` | LLM Wiki (markdown knowledge graph) |
| `haki/rag/` | Retrieval-augmented generation |
| `haki/lab/` | Autoresearch-style fine-tuning |
| `haki/health/` | Metabolic health monitor |
| `haki/self_heal.py` | Autonomous recovery cycle |
| `haki/kaizen.py` | Continuous improvement log |
| `haki/philosophy.py` | Becoming / tensions / questions |
| `haki/organism.py` | Living base class |
| `haki/daemon/` | Message bus + orchestration |
| `haki/mcp/` | MCP tool bridge |
| `haki/cli/` | Click + Rich CLI |

## Documentation

Full docs live in [`docs/`](docs/README.md):

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Philosophy / Becoming](docs/philosophy.md)
- [Kaizen](docs/kaizen.md)
- [API Reference](docs/api.md)
- [Deployment](docs/deployment.md)
- [Contributing](docs/contributing.md)

## Configuration

Environment variables (prefix `HAKI_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_LLM_API_KEY` | `""` | Wide-model API key |
| `HAKI_LLM_API_BASE` | OpenAI | API base URL |
| `HAKI_LLM_MODEL` | `gpt-4o-mini` | Wide model name |
| `HAKI_NARROW_MODEL_ID` | TinyLlama 1.1B | Local model |
| `HAKI_DATA_DIR` | `~/.haki` | Data root |
| `HAKI_LAB_MIN_TRAINING_PAIRS` | `3` | Min pairs before fine-tune |
| `HAKI_HEALTH_INTERVAL` | `30` | Health tick (seconds) |
| `HAKI_SELF_HEAL_INTERVAL` | `300` | Self-heal tick (seconds) |

## License

MIT
