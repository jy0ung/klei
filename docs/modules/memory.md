# Memory Module

Haki's persistent self-learning memory graph, inspired by Honcho.

## Architecture

```
┌─────────────────────────────────────────┐
│               Memory Graph               │
│                                         │
│  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │ Messages │  │ Insights │  │ User   │ │
│  │ (raw)    │  │ (learned)│  │ Model  │ │
│  └─────────┘  └──────────┘  └────────┘ │
│                                         │
│  Backend: SQLite + FAISS vectors         │
│  Embeddings: sentence-transformers       │
└─────────────────────────────────────────┘
```

## Storage

### SQLite Tables

| Table | Purpose |
|-------|---------|
| `memories` | All memory nodes (id, content, role, embedding, metadata, importance) |
| `user_model` | Theory of Mind — psychological profile of the user |
| `interactions` | Raw conversation log (user_input, assistant_output, tier, timestamp) |

### FAISS Index

- Separate index for memory embeddings
- Inner product (cosine similarity after normalization)
- Sidecar JSON for document text storage

## Node Types

| Role | Description |
|------|-------------|
| `user` | User messages |
| `assistant` | Haki responses |
| `system` | System events |
| `insight` | Extracted facts (preferences, name, dislikes) |

## Self-Learning Loop

```
Interaction → store_interaction()
                 ↓
            _extract_insights()
                 ↓
            store_memory() (role="insight")
                 ↓
            Add to FAISS index
                 ↓
            Update user_model
```

## Usage

```python
from haki.memory import memory, MemoryNode
from datetime import datetime

await memory.initialize()

# Store a memory
node = MemoryNode(
    id="fact-1",
    content="User prefers Python over JavaScript",
    role="insight",
    importance=1.0,
)
await memory.store_memory(node)

# Search
results = await memory.search("programming language preference", top_k=5)
for r in results:
    print(f"[{r.role}] {r.content} (importance={r.importance})")

# Log interaction
await memory.learn_from_interaction("I love Python", "I'll remember that!")

# Update user model
await memory.update_user_model(
    theory_of_mind="User is a Python developer who likes concise answers",
    preferences={"language": "Python", "style": "terse"},
    comm_style="technical",
)
```

## Retrieval API

| Method | Description |
|--------|-------------|
| `search(query, top_k)` | Semantic search across all memories |
| `get_all()` | Get all memories ordered by time |
| `get_recent_interactions(n)` | Last N interactions for context |
| `get_user_model()` | Current Theory of Mind model |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `HAKI_RAG_TOP_K` | `5` | Search results count |
| `HAKI_DATA_DIR` | `~/.haki` | DB location |

## Design Decisions

1. **Peer-centric**: memories linked to a single user model (will support multi-peer)
2. **Self-reinforcing**: importance increases with retrieval score
3. **Ephemeral by default**: insights decay unless reinforced
4. **Vector + relational**: FAISS for similarity, SQLite for structured queries

## Limitations

- Single-user only (multi-tenant requires per-user DBs)
- Insight extraction is heuristic, not LLM-based
- No TTL or automatic pruning
- No encryption at rest
