# Lab Module

Autoresearch-style **self-evolution**: train LoRA on memory, keep lower val_bpb, **replace the living brain**.

`Lab(Organism)` — no cloud trainer API.

## Pipeline

```
1. create_training_data_from_memory(allow_seed=True|False)
2. pair count gate (HAKI_LAB_MIN_TRAINING_PAIRS)
3. import torch/transformers/peft only after data OK
4. LoRA fine-tune on HAKI_BASE_MODEL_ID
5. val_bpb ≈ val_loss / ln(2)
6. if NEW BEST and HAKI_LAB_AUTO_PROMOTE:
     promote_to_brain() → brain.promote_adapter + reload
7. log results.tsv
```

## Self-evolution API

```python
from haki.lab import lab

await lab.initialize()

# One cycle (train → maybe replace brain)
result = await lab.evolve_once(epochs=1)
print(result.status, result.val_bpb, result.description_text)

# Multiple cycles
results = await lab.evolve_loop(max_experiments=10)

# Explicit fine-tune
result = await lab.fine_tune_model(allow_seed=True)
```

## Seed data

If interactions &lt; min pairs, Lab seeds domain instruction pairs so evolution can smoke-test offline. Disable with `allow_seed=False`.

## CLI

```bash
haki evolve -n 3 -e 1
haki lab --epochs 1
```

## Outputs

```
~/.haki/lab/
  active_model.json          # living brain pointer
  data/training.jsonl
  models/<exp_id>/adapter/   # LoRA generations
  results.tsv
```

## Defaults (4GB-friendly)

| Config | Default |
|--------|---------|
| `lab_gpu` | `false` (CPU) |
| `lab_auto_promote` | `true` |
| batch | 1 + grad accum 4 |
| max seq | 256 tokens |

## Related

- Karpathy Autoresearch skill  
- [brain.md](brain.md)  
- [architecture.md](../architecture.md)  
