# Lab Module

Autonomous model creation — Haki's ability to build its own specialized model.

Based on [Karpathy's Autoresearch](https://github.com/karpathy/autoresearch) pattern.

## Architecture

```
┌─────────────────────────────────────────┐
│                  Lab                     │
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  Data    │  │ Training│  │  Eval   │ │
│  │ Generator│→ │ (LoRA)  │→ │(val_bpb)│ │
│  └─────────┘  └─────────┘  └─────────┘ │
│       ↑                          │      │
│       └────── Memory Graph ──────┘      │
│                                         │
│  Loop: idea → modify → train → evaluate │
└─────────────────────────────────────────┘
```

## Training Pipeline

1. **Generate data**: Extract interactions from Memory Graph
2. **Tokenize**: Format as `### Instruction:\n...\n\n### Response:\n...`
3. **Fine-tune**: LoRA/PEFT on base model
4. **Evaluate**: Calculate val_bpb (bits per byte)
5. **Keep/Revert**: Based on improvement

## Data Generation

The Lab pulls from `memory_graph.get_recent_interactions()`:

```
# ~/.haki/lab/data/training.jsonl
{"instruction": "What's Python?", "response": "Python is a programming language..."}
{"instruction": "Hello!", "response": "Hi there! How can I help?"}
```

## Training Config

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_NARROW_MODEL_ID` | `TinyLlama-1.1B` | Base model |
| `HAKI_LAB_TIME_BUDGET` | `300` | Seconds per experiment |
| `HAKI_LAB_GPU` | `true` | Use GPU if available |

### LoRA Config

```
LoraConfig(
    task_type=CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
)
```

## Running Experiments

```python
from haki.lab import lab

await lab.initialize()
result = await lab.fine_tune_model(epochs=1)

print(result.id)           # "a1b2c3d"
print(result.val_bpb)      # 0.9979
print(result.status)       # "success"
print(result.description_text)  # "NEW BEST" or error
```

## Autoresearch Loop

```python
# Continuous experiment loop (100 experiments)
await lab.run_autoresearch_loop(max_experiments=100)
```

Generates ideas → runs experiments → keeps best model.

## Results

Logged to `~/.haki/lab/results.tsv`:

```
id      val_bpb     status      description         training_seconds
a1b2c3d 0.997900    success     baseline            45.2
b2c3d4e 0.993200    success     increase LoRA rank  48.1
c3d4e5f 1.005000    failed      switch to GeLU      12.3
```

## Metrics

| Metric | Description |
|--------|-------------|
| `val_bpb` | Validation bits-per-byte (lower is better) |
| `val_loss` | Raw cross-entropy loss |
| `training_seconds` | Wall-clock time |
| `peak_vram_mb` | Max GPU memory used |

## Best Model Tracking

```python
best_path = lab.get_best_model()
# → ~/.haki/lab/models/<id>/adapter/
```

The best LoRA adapter is kept and can be loaded for inference.

## CLI

```bash
# Run one experiment
haki lab --epochs 1

# With specific model
haki lab --model TinyLlama/TinyLlama-1.1B-Chat-v1.0

# View results
cat ~/.haki/lab/results.tsv
```

## Design Decisions

1. **LoRA over full fine-tune**: 100x less memory, faster training
2. **Fixed time budget**: All experiments comparable (5 min default)
3. **Single metric (val_bpb)**: Unambiguous improvement signal
4. **Data from memory**: Learns from real user interactions, not synthetic data

## Limitations

- Single-GPU only (no distributed training)
- No hyperparameter scheduling (fixed ideas list)
- No early stopping apart from time budget
- Training data must be non-empty (needs interactions first)
