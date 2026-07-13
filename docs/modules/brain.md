# Brain Module

The brain is Haki's dual-tier model orchestration layer (`Brain(Organism)`), inspired by CognitiveOS.

## Architecture

```
Query → Brain.think()
           │
     ┌─────┴─────┐
     │ simple?    │
     └──┬─────┬──┘
        │     │
    NARROW   WIDE
   (local)  (remote)
        │     │
     BrainResponse + pulse/error
```

## Routing

Heuristic `_is_simple_query()`: short queries (≤10 words) with common keywords route to **narrow**; otherwise **wide**. Override with `force_tier`.

## Models

- **Narrow:** `HAKI_NARROW_MODEL_ID` (default TinyLlama 1.1B) — optional  
- **Wide:** OpenAI-compatible API via `HAKI_LLM_API_KEY` / `HAKI_LLM_MODEL`  

## Usage

```python
from haki.brain import brain, TierChoice

await brain.initialize()
result = await brain.think("What's the weather?")
print(result.tier, result.text, brain.get_vitality())
```

## Related

- [organism.md](organism.md)  
- [api.md](../api.md)  
