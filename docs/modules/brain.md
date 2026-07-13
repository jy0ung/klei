# Brain Module

Local-only living brain. **No cloud LLM API.**

`Brain(Organism)` loads a tiny base model and optional Lab LoRA adapter, and can **replace itself** when Lab finds a better generation.

## Default model

| Setting | Value |
|---------|--------|
| Base | `HuggingFaceTB/SmolLM2-360M-Instruct` |
| Target hardware | ~4GB-class machines |
| Mode | `local-only` |

Override: `HAKI_BASE_MODEL_ID`.

## Architecture

```
think(query)
    │
    ├─ weights loaded? ──yes──→ local generate (base ± LoRA)
    │
    └─ no ──→ rule-fallback (still offline)
```

Promotion:

```
Lab NEW BEST
  → brain.promote_adapter(path, val_bpb)
  → write active_model.json
  → reload()
  → generation N+1
```

## Registry

`~/.haki/lab/active_model.json` points at the living adapter.

## API

```python
from haki.brain import brain

await brain.initialize()
card = brain.model_card()
# { base_model, adapter_path, generation, val_bpb, loaded, mode: "local-only" }

result = await brain.think("Who are you?")
print(result.text, result.generation, result.model)

# After Lab trains a better adapter:
await brain.promote_adapter(
    adapter_path="~/.haki/lab/models/abc/adapter",
    val_bpb=0.95,
    description="experiment X",
)
```

## CLI

```bash
haki brain
haki chat
haki chat -m "Hello"
```

Chat slash: `/brain`, `/evolve`.

## Health

- **Healthy** if local weights loaded  
- **Degraded** if fallback mode (weights missing / load error)  
- Never requires API key  

## Related

- [lab.md](lab.md) — evolve + promote  
- [architecture.md](../architecture.md)  
