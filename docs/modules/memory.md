# Memory Module

Persistent self-learning memory graph (Honcho-inspired), implemented as `MemoryGraph(Organism)`.

## Backend

- **SQLite** — memories, interactions, user_model  
- **FAISS** — vector index (inner product on L2-normalized embeddings)  
- **sentence-transformers** — embeddings (`HAKI_EMBEDDING_MODEL`)  

Wiki is the primary *compiled* knowledge UI; Memory is the *event + embedding* store.

## Tables

| Table | Purpose |
|-------|---------|
| `memories` | Nodes (content, role, embedding, importance) |
| `interactions` | User/assistant turns + tier |
| `user_model` | Theory of Mind snapshot |

## Roles

`user` · `assistant` · `system` · `insight`

## Self-learning

`learn_from_interaction(user, assistant)`:

1. Stores interaction  
2. Extracts insights via multi-pattern rules (prefs, dislikes, name, goals, constraints, workplace, style)  
3. Stores insight nodes  
4. Updates `user_model` preferences / theory_of_mind  

## Embedding API compat

Uses `_embedding_dim()` which prefers `get_embedding_dimension()` and falls back to legacy `get_sentence_embedding_dimension()`.

## API

```python
from haki.memory import memory, MemoryNode

await memory.initialize()
await memory.learn_from_interaction("I prefer concise answers", "OK")
hits = await memory.search("communication style")
model = await memory.get_user_model()
```

## Design notes

- Single-user peer model for now  
- Importance reinforcement on retrieval  
- Insight extraction is structured heuristics (LLM extraction is a future upgrade)  

## Related

- [wiki.md](wiki.md)  
- [rag.md](rag.md)  
- [organism.md](organism.md)  
