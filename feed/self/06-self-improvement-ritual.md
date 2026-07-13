# Self-Improvement Ritual

A repeatable loop for improving Haki **as Haki** — no external domain data required.

## Phase A — Bootstrap knowledge (once)

```bash
haki init
haki wiki init
haki wiki ingest feed/self/01-identity.md -t "Haki Identity" -e "Haki" -c "identity,local AI,cognitive OS"
haki wiki ingest feed/self/02-commands.md -t "Haki Commands" -e "Haki,CLI" -c "commands,operations"
haki wiki ingest feed/self/03-evolve-lab.md -t "Lab Evolve" -e "Lab,LoRA" -c "self-evolution,val_bpb"
haki wiki ingest feed/self/04-thinking-mastery.md -t "Thinking Mastery" -e "Mastery,SpecializedBrain" -c "research,experiment,mastery"
haki wiki ingest feed/self/05-safety-truth.md -t "Safety Truth" -e "Haki" -c "safety,truthfulness"
haki wiki ingest feed/self/06-self-improvement-ritual.md -t "Self Improvement Ritual" -e "Kaizen,Haki" -c "ritual,kaizen,practice"
haki wiki lint
```

## Phase B — Exercise (create training signal)

Ask the same facts in chat until answers cite wiki/memory:

```text
Who are you?
What is your thinking loop?
When should I run haki evolve?
Where is active_model.json?
What does degraded brain status mean?
How does mastery work?
What must Lab pass for causal LM loss?
```

Aim for **20+ clean turns** before heavy evolve.

## Phase C — Measure

```bash
haki mastery
haki health
haki brain
haki wiki status
```

## Phase D — Evolve

```bash
haki evolve
haki brain          # check generation / adapter
# optional multi-cycle when machine is idle:
haki evolve -n 3
```

## Phase E — Kaizen

After any real fix or learning:

```bash
haki kaizen add -t "short title" -p "what was wrong or missing" -a "what changed" -i "user impact" -c flow
haki kaizen list
```

## Cadence

| Frequency | Action |
|-----------|--------|
| Daily use | `haki chat` / `haki think` on self topics |
| After doc changes | re-ingest changed feed files + short quiz chat |
| After ~20 new good turns | `haki evolve` once |
| Weekly | `haki mastery`, `haki wiki lint`, `haki kaizen stats` |

## Success criteria (self-only)

1. Wiki has the six self pages (or updated versions).  
2. Mastery confidence on `self` / `lab-evolve` rises after practice.  
3. At least one successful Lab run with `val_bpb` set.  
4. Optional: `generation >= 1` after promote.  
5. Health messages are actionable (not opaque failures).

## Anti-patterns

- Evolving with empty memory and no self wiki.  
- Ingesting huge unrelated corpora before self-kernel is solid.  
- Expecting cloud-level tool use from the tiny neural head alone.  
- Rebuilding the Python package after every git pull (use editable install).
