# Haki Documentation

> Local-only cognitive OS: tiny model + Lab self-evolution + memory/wiki/heal.

**Current version:** 0.2.0

## Index

| Document | Description |
|----------|-------------|
| [Quickstart](quickstart.md) | Install, local chat, evolve, heal |
| [Architecture](architecture.md) | System design, self-evolution, storage |
| [Philosophy](philosophy.md) | Becoming / organisms |
| [Kaizen](kaizen.md) | Continuous improvement |
| [Deployment](deployment.md) | Production notes |
| [API Reference](api.md) | Public APIs |
| [Contributing](contributing.md) | Dev + Kaizen cycle |
| [CHANGELOG](CHANGELOG.md) | Version history |

## Module Docs

| Module | File | Purpose |
|--------|------|---------|
| **Brain** | [modules/brain.md](modules/brain.md) | Local model + self-replacement |
| **Cognition** | [modules/cognition.md](modules/cognition.md) | Specialized think loop (research/experiment) |
| **Lab** | [modules/lab.md](modules/lab.md) | Evolve / fine-tune / promote |
| **Memory** | [modules/memory.md](modules/memory.md) | Self-learning graph |
| **Wiki** | [modules/wiki.md](modules/wiki.md) | Compiled knowledge |
| **RAG** | [modules/rag.md](modules/rag.md) | Retrieval |
| **Health** | [modules/health.md](modules/health.md) | Monitoring |
| **Self-Heal** | [modules/self_heal.md](modules/self_heal.md) | Recovery |
| **Organism** | [modules/organism.md](modules/organism.md) | Living base class |
| **Daemon** | [modules/daemon.md](modules/daemon.md) | Bus + loops |
| **MCP** | [modules/mcp.md](modules/mcp.md) | MCP tools |
| **CLI** | [modules/cli.md](modules/cli.md) | Commands |

## Quick Start

```bash
pip install -e .
haki init
haki chat
haki brain
haki evolve -n 1
haki health
```

No cloud API key required.

## Architecture Overview

```
User → CLI
        ↓
 Local Brain (base ± LoRA gen N)
        ↓
 Memory / Wiki / RAG
        ↓
 Lab.evolve → better val_bpb? → promote → gen N+1
        ↑
 Health + Self-heal + Becoming (daemon)
```

See [architecture.md](architecture.md).
