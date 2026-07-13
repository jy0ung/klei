# Haki — Cognitive OS (local-only)

> A cognitive OS that runs a **tiny local model**, improves it in the **Lab**, and **replaces itself** with better versions. **No cloud LLM API.**

**Version:** 0.2.0 · **License:** MIT

## What this is

Haki is a **local-first cognitive runtime**:

1. A small base model runs on this machine (default: SmolLM2-360M — ~4GB-class).
2. Chat and memory feed training data.
3. The **Lab** fine-tunes LoRA adapters (Autoresearch-style, val_bpb).
4. When an adapter is better, it is **promoted** into the living brain.
5. Generation N+1 serves the next chat — the system improves itself.

This is **not** a cloud-API wrapper. Hermes remains the daily agent; Haki is the **local model foundry + cognitive substrate**.

## Self-evolution loop

```
chat / memory interactions
        ↓
   Lab.evolve_once()  (fine-tune LoRA on local base)
        ↓
   better val_bpb?
        ↓ yes
   brain.promote_adapter()  → active_model.json + reload
        ↓
   generation N+1 serves chat
```

## Architecture (summary)

```
┌─────────────────────────────────────────────────────────┐
│                      User (Human)                        │
├─────────────────────────────────────────────────────────┤
│         CLI · MCP · status / heal / evolve / brain       │
├─────────────────────────────────────────────────────────┤
│   hakid — MessageBus + Health + Becoming + SelfHealer    │
├─────────────────────────────────────────────────────────┤
│     Local Brain = base model ± LoRA @ generation N       │
│     (SmolLM2-360M-Instruct · no remote wide API)         │
├─────────────────────────────────────────────────────────┤
│ Memory │ Wiki │ RAG │ Lab │ Health │ Kaizen │ Philosophy │
├─────────────────────────────────────────────────────────┤
│                      Host OS                             │
└─────────────────────────────────────────────────────────┘
```

Full design: [docs/architecture.md](docs/architecture.md)

## Quick Start

```bash
pip install -e .
haki init
haki chat                 # local brain (rule fallback until weights load)
haki brain                # model card: generation, adapter, load state
haki evolve -n 1          # one self-evolution cycle
haki lab                  # fine-tune + auto-promote if best
haki health
haki heal
haki kaizen list
```

No `HAKI_LLM_API_KEY` required.

## Optional config

```bash
# ~/.haki or .env
HAKI_BASE_MODEL_ID=HuggingFaceTB/SmolLM2-360M-Instruct
HAKI_MODEL_CPU=true
HAKI_LAB_GPU=false
HAKI_LAB_AUTO_PROMOTE=true
HAKI_LAB_MIN_TRAINING_PAIRS=3
HAKI_MODEL_MAX_NEW_TOKENS=128
```

## Modules

| Path | Role |
|------|------|
| `haki/brain/` | Local-only brain + promote/reload |
| `haki/lab/` | Evolve / fine-tune / auto-promote |
| `haki/memory/` | Interaction graph + insights |
| `haki/wiki.py` | LLM Wiki knowledge compile |
| `haki/rag/` | Retrieval |
| `haki/health/` + `self_heal.py` | Monitor + recover |
| `haki/kaizen.py` | Continuous improvement log |
| `haki/philosophy.py` | Becoming / tensions |
| `haki/daemon/` | Bus + loops |

## Documentation

- [docs/README.md](docs/README.md) — index  
- [docs/architecture.md](docs/architecture.md) — full architecture  
- [docs/quickstart.md](docs/quickstart.md) — install & first run  
- [docs/api.md](docs/api.md) — API reference  
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — version history  

## License

MIT
