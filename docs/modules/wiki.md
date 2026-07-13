# Wiki Module

LLM-maintained persistent knowledge base, implementing [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Wiki                                    │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Raw Sources  │  │  Wiki Pages  │  │  Schema (schema.md) │  │
│  │ (immutable)  │→ │  (markdown)  │  │  (LLM instructions)  │  │
│  └─────────────┘  └──────────────┘  └──────────────────────┘  │
│                         ↕                                       │
│                  ┌──────────────┐                                │
│                  │ index.md     │  (catalog of all pages)       │
│                  │ log.md       │  (chronological log)           │
│                  └──────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
~/.hiki/wiki/
├── schema.md          # Schema: instructions for LLM discipline
├── index.md           # Catalog of all pages (auto-generated)
├── log.md             # Chronological operation log
├── entities/          # Pages for specific entities (people, places)
├── concepts/          # Pages for ideas, topics
├── sources/           # Source summaries
├── synthesis/         # Cross-cutting syntheses
└── insights/          # Insights from memory graph
```

## Three Layers

### 1. Raw Sources

Immutable source documents — articles, papers, reports. LLM reads from them but never modifies them. Source of truth.

### 2. Wiki Pages

LLM-generated markdown files. Each page has YAML frontmatter:

```yaml
---
title: Python (programming language)
type: entity
tags: [programming, language]
sources: [sources/intro-to-python.md]
created: 2026-07-13T10:00:00
updated: 2026-07-13T12:30:00
importance: 1.0
---

# Python (programming language)

Python is a high-level, general-purpose programming language...
```

Cross-references via `[[wiki links]]` create the graph structure.

### 3. Schema

`schema.md` is the "research org code" — it instructs the LLM on:
- Directory structure conventions
- Frontmatter requirements
- Ingest workflow steps
- Query discipline
- Lint checks

## Operations

### Ingest

```python
result = await wiki.ingest_source(
    source_path="paper.pdf",
    title="Deep Learning Survey",
    entities=["Yann LeCun", "Yoshua Bengio"],
    concepts=["deep learning", "neural networks"],
)
# Creates: sources/paper.pdf, entities/yann-lecun.md, concepts/deep-learning.md
# Updates: index.md, log.md, any existing entity/concept pages
```

Each ingest creates/updates 10-15 pages, cross-linking everything.

### Query

```python
result = await wiki.query("What is Python?", top_k=5)
# Reads: index.md to find relevant pages
# Reads: those page files
# Returns: sources + context for brain synthesis
```

### Lint

```python
result = await wiki.lint()
# Checks:
# - Orphan pages (no inbound links)
# - Stale pages (>30 days without update)
# - Contradictions between pages
# - Missing cross-references
# - Suggested questions to investigate
```

## Page Types

| Type | Directory | Description |
|------|-----------|-------------|
| `entity` | `entities/` | Specific people, places, organizations, tools |
| `concept` | `concepts/` | Ideas, topics, frameworks |
| `source` | `sources/` | Summaries of ingested documents |
| `synthesis` | `synthesis/` | Cross-cutting analyses connecting many pages |
| `insight` | `insights/` | Facts extracted from memory graph |

## Usage

```python
from haki.wiki import wiki

# Initialize (creates schema, dirs)
await wiki.initialize()

# Ingest a document
result = await wiki.ingest_source(
    "article.md",
    title="Article Title",
    entities=["Entity1"],
    concepts=["Topic1"],
)

# Query
result = await wiki.query("What is X?", top_k=5)

# Lint
result = await wiki.lint()

# List all pages
pages = await wiki.get_all_pages()
```

## CLI

```bash
# Initialize wiki
haki wiki init

# Ingest a document
haki wiki ingest report.md --title "Report" --entities "Python,ML" --concepts "programming,AI"

# Query
haki wiki query "What is Python?"

# Lint
haki wiki lint

# Stats
haki wiki status
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `wiki_init` | Initialize wiki directory |
| `wiki_ingest` | Ingest a source document |
| `wiki_query` | Search wiki for relevant pages |
| `wiki_lint` | Check wiki health |

## Integration with Memory Graph

The wiki extends (not replaces) the memory graph:

- **Memory graph**: Raw interaction storage, embeddings, search
- **Wiki**: Structured knowledge ("compiled" facts from memory + sources)

Flow:
```
Interactions → Memory Graph → insights/ pages in Wiki
Documents → Wiki (sources/) → entities/ + concepts/
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_DATA_DIR` | `~/.haki` | Wiki lives at `data_dir/wiki/` |

## Design Decisions

1. **Wiki as primary interface**: Brain queries the wiki first, not raw memory
2. **Markdown files**: Human-readable, Obsidian-compatible, git-trackable
3. **Schema as discipline**: The LLM follows schema.md for consistency
4. **Compounding knowledge**: Every ingest makes the wiki richer — cross-links accumulate
5. **Human curates, LLM maintains**: Human adds sources and asks questions; LLM does all the bookkeeping

## Limitations

- LLM can't natively edit wiki pages (needs agent like Hermes/Codex to call ingest/query/lint)
- No embedding-based search yet (relies on keyword indexing)
- No automatic source fetching or web clipping
- Obsidian not bundled (use as external viewer)
