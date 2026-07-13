# Haki feed — self-improvement only

Six starter documents for **Haki about Haki**. No domain/business content.

## Files

| File | Topic |
|------|--------|
| `self/01-identity.md` | What Haki is / is not |
| `self/02-commands.md` | CLI and slash commands |
| `self/03-evolve-lab.md` | Lab, evolve, promote |
| `self/04-thinking-mastery.md` | Cognitive loop + mastery map |
| `self/05-safety-truth.md` | Honesty, heal limits, secrets |
| `self/06-self-improvement-ritual.md` | Ingest → practice → evolve → kaizen |

## One-shot ingest (from repo root)

```bash
haki wiki init

haki wiki ingest feed/self/01-identity.md -t "Haki Identity" -e "Haki" -c "identity,local AI,cognitive OS"
haki wiki ingest feed/self/02-commands.md -t "Haki Commands" -e "Haki,CLI" -c "commands,operations"
haki wiki ingest feed/self/03-evolve-lab.md -t "Lab Evolve" -e "Lab,LoRA" -c "self-evolution,val_bpb"
haki wiki ingest feed/self/04-thinking-mastery.md -t "Thinking Mastery" -e "Mastery,SpecializedBrain" -c "research,experiment,mastery"
haki wiki ingest feed/self/05-safety-truth.md -t "Safety Truth" -e "Haki" -c "safety,truthfulness"
haki wiki ingest feed/self/06-self-improvement-ritual.md -t "Self Improvement Ritual" -e "Kaizen,Haki" -c "ritual,kaizen,practice"

haki wiki status
haki wiki query "When should I run haki evolve?"
```

Then practice with chat (~20 turns) before `haki evolve`.
