# Health Module

Self-healing subsystem that continuously monitors all Haki components.

## Architecture

```
┌─────────────────────────────────────────┐
│            Health Monitor                │
│                                         │
│  Every 30s (configurable):              │
│                                         │
│  ┌──────────────┐   ┌──────────────┐   │
│  │  check_all()  │──→│ SystemHealth │   │
│  └──────────────┘   └──────────────┘   │
│         │                    │          │
│         ↓                    ↓          │
│  ComponentStatus      Publish event     │
│  per check            to bus            │
│                                         │
└─────────────────────────────────────────┘
```

## Health Checks

| Name | What it checks | Failure mode |
|------|----------------|--------------|
| `brain` | Model availability | No API key, no local model |
| `memory` | DB connectivity | SQLite corruption, disk full |
| `rag` | Index integrity | FAISS file missing/corrupt |
| `disk` | Free space | < 1GB available |
| `bus` | Event flow | Bus deadlocked |

## Custom Checks

```python
from haki.health import monitor

def my_custom_check():
    # Return HealthCheck(name, status, message)
    if something_wrong:
        return HealthCheck(name="custom", status=ComponentStatus.UNHEALTHY, message="Details")
    return HealthCheck(name="custom", status=ComponentStatus.HEALTHY)

monitor.register_check("custom", my_custom_check)
```

## Status Levels

| Level | Meaning | Action |
|-------|---------|--------|
| `healthy` | All good | Continue |
| `degraded` | Partial failure | Log warning, continue |
| `unknown` | State unclear | Investigate |

When any component is unhealthy, overall status becomes unhealthy.

## Auto-Recovery

```python
# Automatic recovery attempt
if report.overall == ComponentStatus.UNHEALTHY:
    for check in report.checks:
        if check.status == ComponentStatus.UNHEALTHY:
            await monitor.attempt_recovery(check.name)
```

Recovery strategies:
- **memory**: Re-initialize SQLite connection
- **rag**: Reload FAISS index from disk
- **brain**: Reload narrow model if possible

## Events

The monitor publishes to `haki.health` every tick:

```python
{
    "overall": "healthy",
    "checks": [
        {"name": "brain", "status": "healthy", "latency_ms": 0.1, "message": "Narrow=True, Wide=True"},
        {"name": "memory", "status": "healthy", "latency_ms": 2.3, "message": "150 memories stored"},
        ...
    ],
    "uptime_seconds": 3600,
    "memory_usage_mb": 256.7
}
```

## CLI

```bash
haki health
```

Output:
```
┌─ Haki Health Report ────────────────────────────┐
│ brain      │ healthy  │ 0.1ms  │ Narrow=True    │
│ memory     │ healthy  │ 2.3ms  │ 150 memories   │
│ rag        │ healthy  │ 0.5ms  │ Index ready    │
│ disk       │ healthy  │ 0.0ms  │ 42.1GB free    │
│ bus        │ healthy  │ 0.0ms  │ 12 recent      │
└──────────────────────────────────────────────────┘
Uptime: 3600s | Memory: 256.7MB
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_HEALTH_INTERVAL` | `30` | Seconds between checks |

## Integration

```python
# In daemon startup
asyncio.create_task(monitor.run())

# Custom handling
async def on_health(event):
    if event.payload["overall"] != "healthy":
        send_alert_to_slack()

bus.subscribe("haki.health", on_health)
```

## Design Decisions

1. **Non-blocking**: Checks run async, can't stall the daemon
2. **Extensible**: Register checks via `register_check()`
3. **Self-contained**: Each check is independent; one failure doesn't break others
4. **Observable**: Published to bus for external monitoring

## Limitations

- No automatic rollback of bad code changes
- No distributed health correlation
- Recovery strategies are limited (re-init only)
- No alerting (Slack/PagerDuty integration needed)
