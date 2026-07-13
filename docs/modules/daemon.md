# Daemon Module

The `hakid` daemon — Haki's central orchestration loop and message bus.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         hakid daemon                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   MessageBus (pub/sub)                   │    │
│  │                                                                 │
│  │  Topics:                                                     │
│  │  haki.start, haki.ready, haki.stop, haki.shutdown       │
│  │  haki.health                                                 │
│  │  brain.response                                              │
│  │  memory.store, memory.search                                 │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌──────────────┐  ┌────────┴────────┐  ┌──────────────────┐  │
│  │ HealthMonitor│  │ Lab (optional)  │  │ MCP Bridge       │  │
│  └──────────────┘  └─────────────────┘  └──────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## MessageBus

The central coordination primitive — async pub/sub.

```python
from haki.daemon.bus import bus, Event

# Subscribe
bus.subscribe("haki.health", my_handler)

# Publish
await bus.publish(Event(topic="test", payload={"msg": "hi"}, source="me"))
```

### Delivery Guarantees

- **At-most-once**: no persistence, no retries
- **In-order**: subscribers called sequentially
- **Fire-and-forget**: `publish_sync()` creates task on running loop

## Event Types

|Topic | Payload | When |
|-------|---------|------|
|`haki.start` | `{}` | Daemon starting |
|`haki.ready` | `{}` | All systems initialized |
|`haki.stop` | `{}` | Daemon stopping |
|`haki.shutdown` | `{}` | User requests stop |
|`haki.health` | `SystemHealth.to_dict()` | Every health interval |
|`brain.response` | `BrainResponse` | After each query |

## Lifecycle

```
1. Startup
   ↓  publish haki.start
   ↓  Initialize subsystems
   ↓  publish haki.ready
   ↓  Start health monitor loop
   ↓
2. Running (event loop)
   ↓  Wait for events
   ↓
3. Shutdown
   ↓  Receive SIGINT/SIGTERM
   ↓  publish haki.stop
   ↓  Cancel tasks
   ↓  Exit
```

## Running

```bash
# Foreground
haki daemon

# Systemd (see deployment.md)
systemctl start hakid

# Docker
docker run -d haki haki daemon
```

## Implementation

### `HakiDaemon`

```python
class HakiDaemon:
    def __init__(self):
        self.monitor = HealthMonitor()
        self._tasks: list[asyncio.Task] = []

    async def start(self):
        # Publish ready, start health monitor, wait for shutdown
        ...

    async def stop(self):
        # Cancel all tasks, publish stop
        ...
```

### Signal Handling

```python
# Graceful shutdown on SIGINT/SIGTERM
for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_HEALTH_INTERVAL` | `30` | Health tick interval (seconds) |

## Design Decisions

1. **Process-per-user**: One daemon per Haki instance (multi-tenant)
2. **Async core**: All I/O is async; subscribers can be sync or async
3. **Centralized logging**: All events flow through the bus, easy to tap
4. **Graceful shutdown**: Cancels tasks cleanly without data corruption

## Limitations

- Single point of failure (needs supervisor for production)
- No message persistence (events lost on restart)
- No clustering/federation
- No built-in auth for bus subscribers
