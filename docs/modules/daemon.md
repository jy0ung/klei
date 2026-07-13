# Daemon Module

The `hakid` orchestration process — message bus, health, becoming, and self-heal.

## Location

- `haki/daemon/bus.py` — `MessageBus`, `Event`  
- `haki/daemon/main.py` — `HakiDaemon(Organism)`, `run_daemon()`  
- `haki/daemon/__init__.py` — package exports  

## Architecture

```
HakiDaemon(Organism)
  ├── MessageBus (pub/sub)
  ├── HealthMonitor.run()          # continuous
  ├── _becoming_loop()             # ~5 minutes
  └── _self_heal_loop()            # HAKI_SELF_HEAL_INTERVAL
```

## MessageBus

```python
from haki.daemon.bus import bus, Event

bus.subscribe("haki.health", handler)
await bus.publish(Event(topic="haki.health", payload={...}, source="health"))
```

Delivery: at-most-once, sequential subscribers, no persistence.

## Topics

| Topic | When |
|-------|------|
| `haki.start` | Daemon starting |
| `haki.ready` | Subsystems online |
| `haki.stop` / `haki.shutdown` | Teardown |
| `haki.health` | Each health tick |
| `haki.becoming` | Tension scan / proposal |
| `haki.self_heal` | Recovery cycle result |

## Becoming loop

1. Gather wiki/memory/lab/health stats  
2. `becoming.scan_for_tensions`  
3. Generate questions  
4. Propose transformation  
5. Publish `haki.becoming`  

## Self-heal loop

Calls `self_healer.cycle()` on interval. Updates `_last_meaningful_change` when recoveries succeed (used by stasis tension detection).

## CLI

```bash
haki daemon
```

Windows note: signal handlers may be unavailable; stop with Ctrl+C / process kill.

## Related

- [self_heal.md](self_heal.md)  
- [health.md](health.md)  
- [philosophy.md](../philosophy.md)  
