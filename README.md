# Haki — Cognitive OS (local-only)

> A cognitive OS that runs a **tiny local model**, improves it in the **Lab**, and **replaces itself** with better versions. **No cloud LLM API.**

**Version:** 0.2.0 · **License:** MIT

Default base model: `HuggingFaceTB/SmolLM2-360M-Instruct` (4GB-class machines).  
Lab trains LoRA adapters → if `val_bpb` improves → promotes into the living brain (`active_model.json` + hot reload).

## Self-evolution loop

```
chat / memory interactions
        ↓
   Lab.evolve_once()  (fine-tune LoRA on local base)
        ↓
   better val_bpb?
        ↓ yes
   brain.promote_adapter()  → reload living brain
        ↓
   next generation serves chat
```

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
```

No `HAKI_LLM_API_KEY` required.

## Docs

See [docs/README.md](docs/README.md).

## License

MIT
