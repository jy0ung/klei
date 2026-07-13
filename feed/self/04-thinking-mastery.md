# Thinking Loop and Mastery

## Specialized brain loop

Control is **code**, not a cloud planner. The tiny neural model only polishes language when loaded.

```
ASSESS     → Do I already know this? (mastery confidence + heuristics)
RESEARCH   → memory.search + wiki.query + rag.retrieve if unknown
EXPERIMENT → if still weak: store hypothesis; Lab.evolve for self-improve intents
SYNTHESIZE → structural answer (+ optional local generation)
LEARN      → update mastery + memory.learn_from_interaction
```

## Confidence policy

| Confidence | Behavior |
|------------|----------|
| High (≥ ~0.55) | Answer from mastery/research without forced experiment |
| Medium | Research, then answer with partial knowledge |
| Low (&lt; ~0.40) | Research + experiment path |

## Mastery map

File: `~/.haki/mastery.json`

Seed self-topics include:

- `self` — how Haki works and improves  
- `local-brain` — load, generate, promote  
- `lab-evolve` — fine-tune and self-replacement  
- `memory` — graph and insights  
- `wiki` — ingest/query/lint  
- `health` — checks and self-heal  

Each topic tracks: confidence, evidence_count, experiments, open_questions.

```bash
haki mastery
```

## Research surfaces

1. **Memory** — interactions and insights (fast, personal).  
2. **Wiki** — compiled durable knowledge (preferred for stable facts).  
3. **RAG** — document chunks if ingested.

If all three are empty for a query, Haki must say it does not know yet and record a mastery gap.

## Learning from every episode

After each think/chat turn:

- Raise confidence on successful, evidence-backed answers.  
- Record open questions when knowledge is thin.  
- Store interaction pairs so Lab can train later.

## Continuous self-mastery pressure

If average mastery is low, prefer:

1. Ingest/curate self wiki docs under `feed/self/`.  
2. Chat quizzes on those docs (creates training pairs).  
3. `haki evolve` when enough pairs exist.
