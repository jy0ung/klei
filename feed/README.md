# Haki feed — self-improvement only

Six **high-density** starter documents for **Haki about Haki**.  
No business/domain content. Optimized for wiki retrieval + chat quizzes + Lab pairs.

## Files

| File | Topic | Use for |
|------|--------|---------|
| `self/01-identity.md` | What Haki is / living brain / data home | Identity Q&A |
| `self/02-commands.md` | CLI + slash commands | Operations |
| `self/03-evolve-lab.md` | When/how to evolve, labels, promote | Lab self-replacement |
| `self/04-thinking-mastery.md` | Assess→research→experiment→learn | Metacognition |
| `self/05-safety-truth.md` | Honesty, heal limits, health meaning | Safe behavior |
| `self/06-self-improvement-ritual.md` | Full practice loop | Cadence |

Each file includes **Key facts** and **Quiz pairs** for consistent answers.

## One-shot ingest (repo root)

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
haki wiki query "What is the thinking loop?"
```

## After ingest

1. Run the quiz list in `06-self-improvement-ritual.md` via `haki chat` (~20 turns).  
2. `haki mastery` · `haki health` · `haki brain`  
3. `haki evolve` once machine is free.  
4. Re-ingest any file you edit, then short re-quiz.

## Quality rules for future feed edits

- One topic per file · prefer tables + quiz pairs  
- Short sentences · no secrets · no domain data in `feed/self/`  
- Re-ingest after edits · practice before evolve  
