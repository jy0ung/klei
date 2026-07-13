# Quickstart

## Prerequisites

- Python 3.10+
- 8GB+ RAM (16GB recommended)
- Optional: NVIDIA GPU with 6GB+ VRAM for Lab fine-tuning

## Install

```bash
# Clone
git clone https://github.com/jy0ung/klei.git
cd klei

# Install with all dependencies
pip install -e .

# Or minimal install (no GPU/training deps)
pip install -e ".[cpu]"
```

## Initialize

```bash
haki init
```

Creates:
- `~/.haki/data/` — models directory
- `~/.haki/memory.db` — persistent memory
- `~/.haki/lab/` — experiment workspace
- `~/.haki/rag.index` — document index

## Configure

Set environment variables or create `.env` in project root:

```bash
# Required for wide model (LLM API)
HAKI_LLM_API_KEY=sk-...
HAKI_LLM_API_BASE=https://api.openai.com/v1
HAKI_LLM_MODEL=gpt-4o-mini

# Optional overrides
HAKI_NARROW_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0
HAKI_EMBEDDING_MODEL=all-MiniLM-L6-v2
HAKI_LAB_GPU=true
```

## First Chat

```bash
# Single message
haki chat -m "Hello, what can you do?"

# Interactive mode
haki chat
```

Interactive commands:
- `/health` — system status
- `/memory` — show recent memories
- `/search <query>` — semantic search
- `/remember <text>` — store a fact

## Check Health

```bash
haki health
```

Expected output:
```
┌─ Haki Health Report ─────────────┐
│ brain      │ healthy  │ 0.1ms   │
│ memory     │ healthy  │ 2.3ms   │
│ rag        │ healthy  │ 0.5ms   │
│ disk       │ healthy  │ 0.0ms   │
│ bus        │ healthy  │ 0.0ms   │
└──────────────────────────────────┘
```

## Run the Lab

```bash
# Fine-tune on accumulated interactions
haki lab --epochs 1

# View results
cat ~/.haki/lab/results.tsv
```

## Ingest Documents

```bash
haki ingest report.md
haki rag "What does the report say about sales?"
```

## Start Daemon

```bash
haki daemon
```

Keeps message bus running for MCP clients.

## Next Steps

- Read [architecture.md](architecture.md) to understand the system
- See [modules/memory.md](modules/memory.md) for self-learning details
- See [deployment.md](deployment.md) for production setup
