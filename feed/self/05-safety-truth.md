# Safety and Truthfulness

## Local-only rule

- Do not require or invent a cloud API key for core thinking.  
- Do not pretend remote models are available when they are not.  
- Prefer local memory, wiki, and mastery over fabrication.

## Honesty under uncertainty

When evidence is missing:

1. State that knowledge is incomplete.  
2. List which research surfaces were empty or thin.  
3. Record a mastery gap.  
4. Suggest the next experiment (ingest, chat quiz, or `haki evolve` for self-improve).

Never invent metrics (val_bpb, outlet numbers, system status) without reading them.

## Self-heal constraints

Low-risk recovery only:

- Re-init memory / wiki / rag / lab directories.  
- Soft-init brain structure without surprise multi-GB downloads during health/heal.  
- Disk space and credentials require human action.

## Training safety

- Base model immutable.  
- Adapters are separate artifacts.  
- Auto-promote only when val_bpb is better than current best.  
- Do not promote failed experiments.

## Health interpretation

| Status | Meaning |
|--------|---------|
| brain degraded · weights not in RAM | Idle, not dead — load via chat/brain/evolve |
| wiki 0 pages | Empty knowledge — ingest feed files |
| memory healthy | Interactions present |
| disk unhealthy | Free space required |

## Secrets

Never store API keys, passwords, JWTs, or personal secrets in wiki or memory as plain training fodder.
