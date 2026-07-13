# Haki — Cognitive OS

> A fully functional cognitive OS with brain, self-learning, self-healing, and the ability to create its own specialized AI model.

Haki integrates four research pillars into a single autonomous system:

| Pillar | Source | Role |
|--------|--------|------|
| **Brain** | [CognitiveOS](https://cognitive-os.org/) | Dual-tier model orchestration (narrow local + wide remote) |
| **Memory** | [Honcho](https://docs.honcho.to/) | Persistent memory graph with Theory of Mind, self-learning from interactions |
| **RAG** | [AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/) | Retrieval-augmented generation for knowledge grounding |
| **Lab** | [Autoresearch](https://github.com/karpathy/autoresearch) | Autonomous experiment loop that creates specialized models |
| **Health** | — | Self-monitoring, auto-recovery, rollback |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User (Human)                        │
├─────────────────────────────────────────────────────────┤
│                   CLI / TUI (Bubble Tea style)           │
├─────────────────────────────────────────────────────────┤
│                hakid (daemon — message bus)              │
├──────────────────┬──────────────────────────────────────┤
│  Narrow Model    │  Wide Model (LLM API)                 │
│  (local, fast)   │  (remote, capable)                    │
├──────────────────┴──────────────────────────────────────┤
│  Memory Graph  │  RAG Pipeline  │  Lab  │  Self-Healing │
├─────────────────────────────────────────────────────────┤
│                    MCP Bridges                           │
├─────────────────────────────────────────────────────────┤
│                   Host OS (Linux/Win/Mac)                │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install
pip install -e .

# Initialize (creates data dirs, downloads models)
haki init

# Run the daemon
haki daemon start

# Chat with Haki
haki chat

# Run the self-improvement lab
haki lab run

# Check system health
haki health
```

## Modules

- `haki/brain/` — Dual-tier model orchestration
- `haki/memory/` — Persistent self-learning memory graph
- `haki/rag/` — Retrieval-augmented generation
- `haki/lab/` — Autonomous model creation (Autoresearch-style)
- `haki/health/` — Self-healing and monitoring
- `haki/daemon/` — Message bus and orchestration
- `haki/mcp/` — MCP bridge interfaces
- `haki/cli/` — Command-line interface

## License

MIT
