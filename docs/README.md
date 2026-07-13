# Haki Documentation

> Cognitive OS with brain, self-learning, self-healing, and autonomous model creation.

## Index

| Document | Description |
|----------|-------------|
| [Quickstart](quickstart.md) | Install, init, first chat |
| [Architecture](architecture.md) | System design, data flow, modules |
| [Deployment](deployment.md) | Production setup, Docker, config |
| [API Reference](api.md) | Full module/function reference |
| [Contributing](contributing.md) | Dev setup, conventions, testing |

## Module Docs

| Module | File | Purpose |
|--------|------|---------|
| **Brain** | [modules/brain.md](modules/brain.md) | Dual-tier model orchestration |
| **Memory** | [modules/memory.md](modules/memory.md) | Persistent self-learning graph |
| **RAG** | [modules/rag.md](modules/rag.md) | Retrieval-augmented generation |
| **Lab** | [modules/lab.md](modules/lab.md) | Autonomous model creation |
| **Health** | [modules/health.md](modules/health.md) | Self-healing monitor |
| **Daemon** | [modules/daemon.md](modules/daemon.md) | Message bus and orchestration |
| **MCP Bridge** | [modules/mcp.md](modules/mcp.md) | MCP tool interfaces |
| **CLI** | [modules/cli.md](modules/cli.md) | Command-line interface |

## Quick Start

```bash
pip install -e .
haki init
haki chat
```

## Architecture Overview

```
User → CLI/TUI → hakid daemon → Brain (narrow | wide)
                                  ↕
                            Message Bus ← → Memory Graph
                                  ↕
                             RAG Pipeline
                                  ↕
                        Lab  ↔  Health Monitor
                                  ↕
                              MCP Bridges
```

See [architecture.md](architecture.md) for full details.
