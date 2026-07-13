# Specialized Brain (cognition)

Haki's **thinking-for-itself** control loop — not a cloud agent, not raw next-token chat.

## Intent

> If it doesn't know what or how → research.  
> If research is insufficient → experiment.  
> Continuously improve until it masters itself.

## Components

| Module | Role |
|--------|------|
| `haki/cognition.py` | `SpecializedBrain` — metacognitive loop |
| `haki/mastery.py` | Durable competence map (`~/.haki/mastery.json`) |
| `haki/brain/` | Neural local model ± LoRA (optional polish) |
| `haki/lab/` | Experiments that can replace the living model |
| memory / wiki / rag | Research surfaces |

## Loop

```
ASSESS   → mastery confidence + self-knowledge heuristics
RESEARCH → memory.search + wiki.query + rag.retrieve
EXPERIMENT → hypothesis in memory; Lab.evolve_once for self-improve queries
SYNTHESIZE → structural answer (+ local model if loaded)
LEARN    → mastery evidence/gaps + memory.learn_from_interaction
```

## CLI

```bash
haki chat                 # uses specialized loop
haki think "Who are you?" # one episode + full trace
haki mastery              # competence map
haki evolve               # explicit Lab self-replacement
```

## Why specialized (not “just SmolLM”)

Tiny models **cannot** reliably self-orchestrate tools and experiments.  
Haki’s specialized brain puts **control in code** and uses the tiny model for language polish when available. Mastery + research + experiment are **always** available offline.

## Related

- [architecture.md](../architecture.md)  
- [brain.md](brain.md)  
- [lab.md](lab.md)  
