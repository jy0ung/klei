# Haki Documentation

> Cognitive OS with brain, self-learning, self-healing, becoming, and Kaizen.

**Current version:** 0.1.2

## Index

| Document | Description |
|----------|-------------|
| [Quickstart](quickstart.md) | Install, init, first chat, heal, kaizen |
| [Architecture](architecture.md) | System design, data flow, storage |
| [Philosophy](philosophy.md) | Becoming architecture (living organisms) |
| [Kaizen](kaizen.md) | Continuous improvement process |
| [Deployment](deployment.md) | Production, Docker, systemd |
| [API Reference](api.md) | Module/function reference |
| [Contributing](contributing.md) | Dev setup, tests, Kaizen cycle |
| [CHANGELOG](CHANGELOG.md) | Version history |

## Module Docs

| Module | File | Purpose |
|--------|------|---------|
| **Brain** | [modules/brain.md](modules/brain.md) | Dual-tier model orchestration |
| **Memory** | [modules/memory.md](modules/memory.md) | Self-learning memory graph |
| **Wiki** | [modules/wiki.md](modules/wiki.md) | LLM-maintained knowledge base |
| **RAG** | [modules/rag.md](modules/rag.md) | Retrieval-augmented generation |
| **Lab** | [modules/lab.md](modules/lab.md) | Autonomous model creation |
| **Health** | [modules/health.md](modules/health.md) | Metabolic monitoring |
| **Self-Heal** | [modules/self_heal.md](modules/self_heal.md) | Autonomous recovery cycle |
| **Organism** | [modules/organism.md](modules/organism.md) | Living base class |
| **Daemon** | [modules/daemon.md](modules/daemon.md) | Bus + becoming + self-heal |
| **MCP** | [modules/mcp.md](modules/mcp.md) | MCP tool interfaces |
| **CLI** | [modules/cli.md](modules/cli.md) | Command-line interface |

## Quick Start

```bash
pip install -e .
haki init
haki chat
haki health
haki heal
haki kaizen list
```

## Architecture Overview

```
User → CLI/TUI → hakid daemon
                    ├── Health monitor (30s)
                    ├── Becoming loop (5m)
                    └── Self-heal loop (5m)
                           ↕ message bus
         Brain ⇄ Memory ⇄ Wiki ⇄ RAG ⇄ Lab ⇄ Kaizen
```

See [architecture.md](architecture.md) for full details.
