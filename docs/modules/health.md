# Health Module

Metabolic health monitoring + recovery hooks. `HealthMonitor(Organism)`.

## Checks

| Name | Meaning |
|------|---------|
| `brain` | Narrow loaded and/or wide configured |
| `memory` | DB readable, node count |
| `rag` | Index presence |
| `wiki` | Page count |
| `disk` | Free space (unhealthy if < 1GB) |
| `bus` | Recent events |

Statuses: `healthy` · `degraded` · `unhealthy` · `unknown`

## Recovery

`attempt_recovery(component)` re-inits memory/wiki/rag/lab; for brain, avoids heavy downloads.

Prefer `haki heal` / `SelfHealer.cycle()` for full recovery orchestration + audit.

## CLI

```bash
haki health
```

## Continuous run

Daemon calls `monitor.run()` on `HAKI_HEALTH_INTERVAL` (default 30s) and publishes `haki.health`.

## Related

- [self_heal.md](self_heal.md)  
- [daemon.md](daemon.md)  
