# Quickstart

## Prerequisites

- Python 3.10+
- 8GB+ RAM (16GB recommended)
- Optional: NVIDIA GPU for Lab fine-tuning / narrow model

## Install

```bash
git clone https://github.com/jy0ung/klei.git
cd klei
pip install -e .
# optional dev tools
pip install -e ".[dev]"
```

## Initialize

```bash
haki init
```

Creates under `~/.haki/` (or `HAKI_DATA_DIR`):

- `models/` — model cache  
- `memory.db` — memory graph  
- `lab/` — experiments  
- `wiki/` — after `haki wiki init`  
- `kaizen.jsonl` — after first kaizen seed/list  

## Configure

`.env` or environment:

```bash
HAKI_LLM_API_KEY=sk-...
HAKI_LLM_API_BASE=https://api.openai.com/v1
HAKI_LLM_MODEL=gpt-4o-mini
# optional
HAKI_NARROW_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0
HAKI_LAB_MIN_TRAINING_PAIRS=3
```

Without `HAKI_LLM_API_KEY`, wide-model chat returns a configuration error (narrow may still load if weights are available).

## First Chat

```bash
# Single message
haki chat -m "Hello, what can you do?"

# Interactive
haki chat
```

Slash commands in interactive mode:

- `/health` — health report  
- `/memory` — recent memories  
- `/search <query>` — semantic search  
- `/remember <text>` — store insight  

## Health & Self-Heal

```bash
haki health
haki heal          # one autonomous recovery cycle (low-risk)
```

## Kaizen

```bash
haki kaizen list
haki kaizen stats
haki kaizen add -t "title" -p "problem" -a "action" -i "impact" -c defect
```

## Wiki

```bash
haki wiki init
haki wiki ingest notes.md --title "Notes" --entities "Haki" --concepts "cognitive OS"
haki wiki query "What is Haki?"
haki wiki lint
haki wiki status
```

## Lab

```bash
# Uses real interactions if present; otherwise seeds baseline pairs
haki lab --epochs 1
cat ~/.haki/lab/results.tsv
```

## Becoming

```bash
haki become status      # tensions
haki become question    # system question
haki become propose     # transformation proposal
haki status             # organism vitality table
```

## Daemon

```bash
haki daemon
```

Runs:

- health monitor (`HAKI_HEALTH_INTERVAL`, default 30s)  
- becoming loop (5m)  
- self-heal loop (`HAKI_SELF_HEAL_INTERVAL`, default 300s)  

Stop with Ctrl+C.

## Tests

```bash
pytest tests/ -v
```

## Next

- [Architecture](architecture.md)  
- [Philosophy](philosophy.md)  
- [Kaizen](kaizen.md)  
- [API](api.md)  
