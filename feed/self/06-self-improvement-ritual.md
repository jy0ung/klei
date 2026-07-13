# Self-Improvement Ritual

**Tags:** ritual · kaizen · practice · self-only  
**Entities:** Haki, Kaizen, Lab, Wiki  
**Concepts:** ingest, quiz, measure, evolve, no domain data

## Scope

This ritual improves **Haki about Haki only**.  
Do **not** mix external business/domain corpora until the self-kernel is solid.

## Phase A — Bootstrap knowledge (once per machine / after feed updates)

From **repo root** (where `feed/` lives):

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
haki wiki status
```

Re-run ingest for any file you edit later (wiki compiles sources; re-ingest refreshes pages).

## Phase B — Exercise (create Lab training signal)

Use `haki chat` or `haki think`. Prefer short, factual Q&A. Target **≥20 clean turns**.

### Standard quiz set

```text
Who are you?
What is Haki in one sentence?
What is your thinking loop?
When should I run haki evolve?
When should I NOT run haki evolve?
Where is active_model.json?
What is val_bpb and is lower better?
What must Lab pass so the Trainer gets a loss?
What does brain degraded weights not in RAM mean?
Where is mastery stored and how do I view it?
What is immutable — base or LoRA?
Do I rebuild after every git pull?
Name three research surfaces.
What is the core promise when you do not know something?
```

Good answers should track **wiki/memory**, not invent.

## Phase C — Measure

```bash
haki mastery
haki health
haki brain
haki wiki status
haki wiki query "When should I run haki evolve?"
```

Healthy self-progress:

- Wiki page count reflects six self docs (plus derived entity/concept pages).  
- Mastery on `self` / `lab-evolve` not stuck at floor after practice.  
- Query returns relevant self pages.

## Phase D — Evolve

```bash
haki evolve
haki brain
# optional when idle:
haki evolve -n 3 -e 1
```

Pass criteria:

- `status=success` and numeric `val_bpb`, **or** clear fixed error (not silent).  
- Optional: `generation >= 1` and `adapter_path` set after promote.

If fail with logits/no loss → training labels bug; fix Lab before more evolve.

## Phase E — Kaizen

After real learning or a fix:

```bash
haki kaizen add -t "short title" -p "gap or defect" -a "what we did" -i "impact" -c flow
haki kaizen list
```

Categories: `defect` | `waste` | `flow` | `standardization` | `measurement` | `general`

## Cadence

| When | Action |
|------|--------|
| Daily | Chat/think on self quiz topics |
| After editing feed files | Re-ingest those files + 5 quiz turns |
| After ~20 new good turns | `haki evolve` once |
| Weekly | `mastery` + `wiki lint` + `kaizen stats` |

## Success criteria (self-only)

1. All six `feed/self` docs ingested.  
2. Quiz answers consistent with feed.  
3. ≥1 successful Lab metric (`val_bpb`).  
4. Optional promote: generation ≥ 1.  
5. Health messages actionable (idle vs broken).  
6. No domain/business data mixed into this phase.

## Anti-patterns

- Evolve with empty self wiki and no practice turns.  
- Giant unrelated dumps before self-kernel.  
- Expecting Hermes-level tool use from tiny neural head alone.  
- `pip install` / rebuild after every pull (use editable install).  
- Treating HF log noise / faiss AVX2 warnings as hard failures.

## Quiz pairs

**Q:** What is the self-improvement order?  
**A:** Ingest self feed → quiz chat → measure mastery/health/wiki → evolve → kaizen.

**Q:** How many clean practice turns before evolve?  
**A:** About twenty or more on self topics after ingest.

**Q:** What is out of scope for this ritual?  
**A:** External domain/business corpora — self-kernel first only.
