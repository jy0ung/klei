# Thinking Loop and Mastery

**Tags:** SpecializedBrain · mastery · research · experiment  
**Entities:** SpecializedBrain, MasteryStore  
**Concepts:** assess, research, experiment, synthesize, learn, confidence

## One-line definition

Haki’s **specialized brain** is a code-controlled metacognitive loop. The tiny neural model is optional polish; **knowing and improving** are structural.

## Loop (always in this order)

```
ASSESS     → mastery confidence + self-knowledge heuristics
RESEARCH   → memory.search + wiki.query + rag.retrieve   (if not confident)
EXPERIMENT → if still weak: hypothesis in memory; Lab.evolve for self-improve intents
SYNTHESIZE → structural answer (+ local model if weights loaded)
LEARN      → mastery update + memory.learn_from_interaction
```

CLI:

- Full loop in chat: `haki chat`  
- One traced episode: `haki think "..."`  
- Skip experiment: `haki chat --no-experiment`

## Confidence policy

| Band | Approx | Behavior |
|------|--------|----------|
| High | ≥ 0.55 | Answer without forced experiment |
| Medium | ~0.40–0.55 | Research, then answer (partial OK) |
| Low | < 0.40 | Research + experiment path |

Self-identity questions (who are you / what is Haki) start with **boosted** confidence so the system can state its own design clearly.

## Mastery map

**File:** `~/.haki/mastery.json`  
**CLI:** `haki mastery`

### Seed self-topics

| id | Meaning |
|----|---------|
| `self` | How Haki works and improves |
| `local-brain` | Load, generate, promote |
| `lab-evolve` | Fine-tune and self-replacement |
| `memory` | Graph and insights |
| `wiki` | Ingest, query, lint |
| `health` | Checks and self-heal |

Each topic tracks: `confidence`, `evidence_count`, `experiments`, `successes`, `failures`, `open_questions`, `last_practiced`.

### Updates after each episode

- Evidence-backed answer → confidence **up** slightly.  
- Thin answer → open question recorded, confidence may **dip**.  
- Experiment success/failure → experiment counters + confidence adjust.

## Research surfaces (order of use)

1. **Memory** — recent interactions/insights (personal, fast).  
2. **Wiki** — durable compiled facts (preferred for stable self-docs).  
3. **RAG** — ingested document chunks (if any).

If all empty: say **I do not know yet**, record mastery gap, suggest ingest/quiz/evolve.

## Learning signal for Lab

Every good chat turn becomes a future `training.jsonl` pair:

```text
instruction = user question
response   = Haki answer
```

That is why **quiz practice after wiki ingest** matters more than raw file size.

## Continuous self-mastery pressure

If average mastery is low:

1. Re-ingest/curate `feed/self/*.md`.  
2. Chat quiz (list in ritual doc).  
3. `haki evolve` when pair count is healthy.

## Quiz pairs

**Q:** What is the thinking loop?  
**A:** Assess → research → experiment → synthesize → learn.

**Q:** Who controls the loop — cloud LLM or code?  
**A:** Code (SpecializedBrain). Local neural model only polishes language when loaded.

**Q:** Where is mastery stored?  
**A:** `~/.haki/mastery.json`; inspect with `haki mastery`.

**Q:** What if memory, wiki, and RAG are empty?  
**A:** Admit incomplete knowledge, record a gap, suggest ingest and practice — do not invent.
