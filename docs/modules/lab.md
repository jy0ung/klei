# Lab Module

Autonomous model creation (Autoresearch-style), `Lab(Organism)`.

## Pipeline

1. Build `training.jsonl` from memory interactions  
2. If pairs < `HAKI_LAB_MIN_TRAINING_PAIRS`, **seed** baseline domain pairs (unless `allow_seed=False`)  
3. Fail fast before torch/transformers import if still empty / under threshold  
4. LoRA fine-tune  
5. Approximate `val_bpb = val_loss / log(2)`  
6. Log `results.tsv`, keep best adapter  

## Seed pairs

When chat history is thin, Lab seeds instruction pairs about Haki itself (what it is, health, becoming, kaizen, fine-tune prerequisites). This makes Lab smoke-testable immediately.

## API

```python
from haki.lab import lab

await lab.initialize()
path = await lab.create_training_data_from_memory(allow_seed=True)
n = lab.training_pair_count(path)
result = await lab.fine_tune_model(epochs=1, allow_seed=True)
print(result.status, result.val_bpb, result.description_text)
```

## CLI

```bash
haki lab
haki lab --epochs 1 --model TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

## Outputs

```
~/.haki/lab/
  data/training.jsonl
  models/<exp_id>/adapter/
  results.tsv
  logs/
```

## Metrics

| Metric | Meaning |
|--------|---------|
| `val_bpb` | bits-per-byte proxy (lower better) |
| `val_loss` | CE loss |
| `training_seconds` | wall time |
| `peak_vram_mb` | CUDA peak if available |

## Related

- Autoresearch skill / Karpathy loop  
- [memory.md](memory.md)  
- [kaizen.md](../kaizen.md)  
