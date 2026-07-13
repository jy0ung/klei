# RAG Module

Retrieval-Augmented Generation pipeline based on AWS RAG patterns.

## Pipeline

```
Query
  │
  ├─→ Embedding (sentence-transformers)
  │
  ├─→ Memory Search (episodic context)
  │      └─→ FAISS: memory.db.faiss
  │
  ├─→ Document Search (static knowledge)
  │      └─→ FAISS: memory.db.docs.faiss
  │
  ├─→ Merge + Rank
  │      └─→ Sort by score
  │
  └─→ Augmented Prompt
         └─→ Brain.think(augmented)
```

## Sources

| Source | Content | Search |
|--------|---------|--------|
| Memory graph | Past interactions, insights | FAISS vector index |
| Documents | Ingested files (ingested via `haki ingest`) | FAISS doc index |
| Web (future) | Search results | External API |

## Document Ingestion

```python
# Programmatic
await rag.add_document("Long text...", source="book_chapter_1")

# CLI
haki ingest report.md
```

### Chunking

```
Text → words → chunks of N words (overlap 50)
     → embeddings via sentence-transformers
     → FAISS index (inner product)
     → Sidecar JSON (original text)
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_RAG_CHUNK_SIZE` | `512` | Words per chunk |
| `HAKI_RAG_TOP_K` | `5` | Retrieved chunks |
| `HAKI_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |

## Usage

```python
from haki.rag import rag

await rag.initialize()

# Add knowledge
await rag.add_document("Haki is a cognitive OS...", source="README")

# Retrieve
result = await rag.retrieve("What is Haki?", top_k=5)
print(result.augmented_prompt)
print(result.retrieved_chunks)  # [{text, source, score}]
```

## Augmented Prompt Format

```
Based on the following context, answer the user's question.

Context:
[Context 1 from memory]: The user is a developer
[Context 2 from document]: Haki is a cognitive OS...

User question: What is Haki?

Answer (citing sources where applicable):
```

## Integration with Brain

The CLI's `/rag` command shows retrieved chunks. In production:

```python
rag_result = await rag.retrieve(query)
response = await brain.think(rag_result.augmented_prompt)
```

## Design Decisions

1. **Hybrid retrieval**: Memory (episodic) + Documents (semantic)
2. **FAISS for speed**: Inner product on normalized vectors = cosine similarity
3. **Chunk overlap**: 50 words overlap preserves sentence boundaries
4. **Sidecar JSON**: Raw texts stored alongside FAISS for retrieval

## Limitations

- No web search integration yet
- No re-ranking of results
- Chunk splitting is word-level (not semantic)
- No multi-hop retrieval
