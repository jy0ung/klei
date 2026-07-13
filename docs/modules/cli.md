# CLI Module

Rich + Click interface for local-only Haki.

## Commands (v0.2.0)

```
haki init
haki daemon
haki chat [-m MSG]
haki brain
haki evolve [-e EPOCHS] [-n LOOPS]
haki lab [-m MODEL] [-e EPOCHS]
haki health
haki heal
haki status
haki rag <query>
haki ingest <path>
haki wiki init|ingest|query|lint|status
haki become status|question|propose
haki kaizen list|add|stats
```

## Chat (local)

```bash
haki chat
haki chat -m "Who are you?"
```

Slash commands:

| Command | Action |
|---------|--------|
| `/brain` | Model card |
| `/evolve` | One evolution cycle |
| `/health` | Health table |
| `/memory` | Recent memories |
| `/search <q>` | Memory search |
| `/remember <text>` | Store insight |

No `--tier` / no API options.

## Evolve

```bash
haki evolve
haki evolve -n 5 -e 1
```

## Brain card

```bash
haki brain
```

## Implementation notes

- `lab_mod` / `rag_mod` import aliases avoid shadowing command names  
- Async modules bridged via `asyncio.run`  

## Related

- [quickstart.md](../quickstart.md)  
- [api.md](../api.md)  
