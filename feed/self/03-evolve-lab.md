# Lab and Self-Evolution

**Tags:** Lab · evolve · LoRA · val_bpb · Autoresearch  
**Entities:** Lab, LoRA, active_model.json  
**Concepts:** self-replacement, promote, generation, training pairs, fixed budget

## Purpose

Lab creates **specialized versions of Haki** by fine-tuning LoRA on interaction data, measuring quality, and **replacing the living brain** when better.

Pattern: **Autoresearch-style** — experiment → measure → keep/discard → promote if best.

## When to run `haki evolve`

### Do run

- After real chat practice (target **~20+ clean turns** on self topics).  
- After ingesting/updating `feed/self/*` and quizzing those facts.  
- When `haki mastery` shows low confidence on `self`, `lab-evolve`, `local-brain`.  
- When you deliberately want generation N+1.  
- On an idle machine (CPU fine-tune can take minutes).

### Do not run

- On every single chat message.  
- With empty memory **and** no self wiki (seed-only is weak specialization).  
- Expecting overnight GPU Autoresearch quality on first boot with no data.

## Pipeline (exact)

```
1. training.jsonl ← memory interactions (+ seed pairs if thin)
2. Fail-fast if pairs < min (default 3)
3. Import torch/transformers/peft only after data OK
4. LoRA on same base as brain (SmolLM2-360M-Instruct by default)
5. Train; val_bpb ≈ train_loss / ln(2)   # lower is better
6. If NEW BEST and auto-promote:
     active_model.json ← adapter path + generation
     brain.promote_adapter → reload
7. Append lab/results.tsv
```

## Critical training rule (do not forget)

Causal LM **must** supply **`labels`**.

- `labels = input_ids` with pad tokens set to **-100**.  
- Without labels:  
  `The model did not return a loss from the inputs, only the following keys: logits`  
  → experiment **failed**; no promote.

## Artifacts

| Path | Meaning |
|------|---------|
| `lab/data/training.jsonl` | `instruction` / `response` lines |
| `lab/models/<exp_id>/adapter/` | LoRA for one run |
| `lab/active_model.json` | Living brain registry |
| `lab/results.tsv` | id, val_bpb, status, description (do not treat as source of secrets) |

## Base model rules

| Rule | Detail |
|------|--------|
| Default base | `HuggingFaceTB/SmolLM2-360M-Instruct` |
| Immutable base | Never overwrite base checkpoint |
| Adapter only | Promote LoRA path into living brain |
| Device | CPU default (`HAKI_LAB_GPU=false` until measured) |
| Batch | Small (batch 1 + grad accum) for low RAM |

## Success checklist after evolve

```bash
haki brain
# Want: status success earlier; val_bpb set; optional generation>=1 + adapter_path
```

| Signal | Meaning |
|--------|---------|
| `status=success` + `val_bpb=...` | Training produced a metric |
| `NEW BEST + PROMOTED gen=N` | Self-replacement happened |
| `adapter_path` set on model card | Living brain points at LoRA |
| `failed` + loss/logits error | Labels/training bug or env issue — fix before re-evolve |

## Relation to chat

- Specialized brain may experiment with **hypotheses** on hard questions.  
- Lab **evolve** from chat only for clear self-improve intents (or `/evolve`).  
- Explicit `haki evolve` is the deliberate self-replacement path.

## Quiz pairs

**Q:** When should I run haki evolve?  
**A:** After ~20 clean practice turns and self wiki ingest, or when mastery on self-topics is low — not every chat message.

**Q:** What metric decides keep/promote?  
**A:** val_bpb (approx train_loss/ln2); lower is better; promote only if best.

**Q:** Why did train fail with only logits?  
**A:** Missing labels for causal LM; labels must be input_ids with pad masked to -100.

**Q:** What file points at the living adapter?  
**A:** `~/.haki/lab/active_model.json`.
