# Quickstart

## Prerequisites

- Python 3.10+
- **4GB+ RAM** for default SmolLM2-360M (8GB+ more comfortable)
- Optional: NVIDIA GPU for faster Lab fine-tunes (`HAKI_LAB_GPU=true`)
- Disk for HF model cache under `~/.haki/models/`

## Install

```bash
git clone https://github.com/jy0ung/klei.git
cd klei
pip install -e .
pip install -e ".[dev]"   # optional tests
```

## Initialize

```bash
haki init
```

Creates `~/.haki/` (or `HAKI_DATA_DIR`):

- `models/` — base model cache  
- `memory.db` — memory graph  
- `lab/` — experiments + `active_model.json`  
- `wiki/` — after `haki wiki init`  

## Configure (optional)

**No API key required.** Local-only defaults:

```bash
# .env
HAKI_BASE_MODEL_ID=HuggingFaceTB/SmolLM2-360M-Instruct
HAKI_MODEL_CPU=true
HAKI_LAB_GPU=false
HAKI_LAB_AUTO_PROMOTE=true
HAKI_LAB_MIN_TRAINING_PAIRS=3
HAKI_MODEL_MAX_NEW_TOKENS=128
```

## First chat (local)

```bash
haki chat -m "Who are you?"
haki chat
```

Until base weights finish downloading, Haki answers in **rule-fallback** mode (still offline).

Interactive extras:

- `/brain` — model card  
- `/evolve` — one Lab evolution cycle  
- `/health`, `/memory`, `/search`, `/remember`  

## Brain status

```bash
haki brain
```

Shows base model, adapter path, generation, loaded flag, load errors.

## Self-evolution

```bash
# One cycle: train on memory → promote if better
haki evolve

# Several cycles
haki evolve -n 5 -e 1

# Explicit lab fine-tune
haki lab --epochs 1
```

Results: `~/.haki/lab/results.tsv`  
Living pointer: `~/.haki/lab/active_model.json`

## Health & self-heal

```bash
haki health
haki heal
```

## Wiki & Kaizen

```bash
haki wiki init
haki wiki ingest notes.md --entities "Haki" --concepts "local AI"
haki kaizen list
```

## Daemon

```bash
haki daemon
```

Runs health + becoming + self-heal loops. Stop with Ctrl+C.

## Tests

```bash
pytest tests/ -v
```

## Next

- [Architecture](architecture.md) — full design  
- [Brain](modules/brain.md) · [Lab](modules/lab.md)  
- [CHANGELOG](CHANGELOG.md)  
