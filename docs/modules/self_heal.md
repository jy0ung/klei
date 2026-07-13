# Self-Heal Module

Autonomous recovery for Haki subsystems (L2 post-hoc self-healing).

## Location

`haki/self_heal.py` — `SelfHealer(Organism)` singleton `self_healer`

## Design

```
Health checks find degraded/unhealthy components
        ↓
SelfHealer.recover(component)  # low-risk only
        ↓
Publish haki.self_heal on bus
        ↓
Record kaizen entry if any recovery succeeded
```

### Low-risk rules

| Component | Auto recovery |
|-----------|---------------|
| `memory` | Re-init SQLite + embeddings |
| `wiki` | Re-init wiki dirs/schema |
| `rag` | Re-init document index |
| `lab` | Re-init lab directories |
| `brain` | Mark initialized for API mode; **does not** download TinyLlama |
| `disk` | Escalate (cannot free space automatically) |
| `bus` | Soft-state; no hard recovery |

## API

```python
from haki.self_heal import self_healer

result = await self_healer.cycle()
# {
#   "overall": "healthy|degraded|unhealthy",
#   "actions": [...],
#   "recovered": N,
#   "failed": M,
#   "message": "..."  # when no actions
# }

action = await self_healer.recover("memory")
history = self_healer.history(n=20)
```

## CLI

```bash
haki heal
```

## Daemon integration

`HakiDaemon` runs `_self_heal_loop` every `HAKI_SELF_HEAL_INTERVAL` (default 300s).

Subscribes to `haki.self_heal` and updates last meaningful change time when recoveries succeed.

## Health integration

`HealthMonitor.attempt_recovery` covers the same components for on-demand recovery.

## Safety

- No recursive code mutation in v0.1.2  
- No automatic large model downloads  
- Human still required for disk/API credentials  
- Audit trail via bus events + optional kaizen records  

## Related

- [health.md](health.md)  
- [daemon.md](daemon.md)  
- [kaizen.md](../kaizen.md)  
- Self-healing agent architecture pattern (Hermes skill reference)  
