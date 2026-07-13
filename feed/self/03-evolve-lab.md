# Lab and Self-Evolution

## Purpose

The Lab is how Haki **creates specialized versions of itself** without cloud training APIs.

Pattern: Autoresearch-style fixed-budget experiment → measure → keep or discard → **promote** if better.

## When to run `haki evolve`

**Do run** when:

- There are real chat interactions (not only first boot).
- Self-knowledge or wiki self-docs were recently ingested and exercised in chat.
- `haki mastery` shows low confidence on self-topics (self, lab-evolve, local-brain).
- You deliberately want a new LoRA generation.

**Do not run** on every chat turn. Evolve is heavier than think/research.

## Pipeline

```
1. Build training.jsonl from memory interactions
2. If thin history → seed domain pairs about Haki itself (allow_seed)
3. Fail-fast if still empty / under min pairs
4. LoRA fine-tune on the same base model the brain serves
5. val_bpb ≈ train_loss / ln(2)   (lower is better)
6. If NEW BEST and lab_auto_promote:
     write lab/active_model.json
     brain.promote_adapter → hot reload
     generation N → N+1
7. Log lab/results.tsv
```

## Critical training rule

Causal LM training **must** pass `labels` (input_ids with pad → -100).  
Without labels, the Trainer fails: *model did not return a loss, only logits*.

## Artifacts

| Path | Meaning |
|------|---------|
| `lab/data/training.jsonl` | Instruction/response pairs |
| `lab/models/<id>/adapter/` | LoRA adapter for one experiment |
| `lab/active_model.json` | Living brain pointer (base + adapter + generation) |
| `lab/results.tsv` | Experiment log (keep untracked) |

## Base model rules

- Default base: `HuggingFaceTB/SmolLM2-360M-Instruct` (~4GB-class).
- Never overwrite base weights; only attach/replace LoRA.
- CPU-first by default (`HAKI_LAB_GPU=false` until measured).

## Success signals after evolve

```bash
haki brain
# generation >= 1 and/or adapter_path set → promotion worked
# status success + val_bpb set → training computed a metric
```

## Relation to specialized brain

Chat may **experiment** with hypotheses or call Lab only for clear self-improve intents.  
Explicit `haki evolve` is the deliberate self-replacement path.
