# CLI Module

Rich-based command-line interface for Haki.

## Commands (v0.1.2)

```
haki init
haki daemon
haki chat [-m MSG] [--tier narrow|wide]
haki health
haki heal
haki status
haki lab [-m MODEL] [-e EPOCHS]
haki rag <query>
haki ingest <path>
haki wiki init|ingest|query|lint|status
haki become status|question|propose
haki kaizen list|add|stats
```

## Chat

```bash
haki chat
haki chat -m "What is Haki?"
haki chat --tier wide -m "Explain the architecture"
```

Interactive slash commands:

| Command | Action |
|---------|--------|
| `/health` | Health table |
| `/memory` | Recent memories |
| `/search <q>` | Memory search |
| `/remember <text>` | Store insight |
| `quit` / `exit` | Leave |

## Health & Heal

```bash
haki health
haki heal
```

## Status (organisms)

```bash
haki status
```

Shows Daemon / Wiki / Brain / Lab stage + ops + errors.

## Wiki

```bash
haki wiki init
haki wiki ingest file.md -t "Title" -e "Entity1,Entity2" -c "Concept1"
haki wiki query "question" -k 5
haki wiki lint
haki wiki status
```

## Becoming

```bash
haki become status
haki become question
haki become propose
```

## Kaizen

```bash
haki kaizen list -n 20
haki kaizen stats
haki kaizen add -t "..." -p "..." -a "..." -i "..." -c defect
```

## Lab

```bash
haki lab
haki lab --epochs 1 --model TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

Uses memory interactions; seeds baseline pairs if history is thin.

## Implementation notes

- Click group + Rich panels/tables  
- Module imports use aliases (`lab_mod`, `rag_mod`) to avoid shadowing CLI command names  
- Async modules bridged via `asyncio.run`  

## Related

- [api.md](../api.md)  
- [quickstart.md](../quickstart.md)  
