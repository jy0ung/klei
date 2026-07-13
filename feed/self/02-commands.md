# Haki Commands

**Tags:** CLI · operations · commands  
**Entities:** Haki, CLI  
**Concepts:** chat, think, evolve, wiki, mastery, health, kaizen, daemon

## Install (once)

```bash
pip install -e .     # editable — code updates usually need no reinstall
git pull             # get latest
# reinstall only if pyproject dependencies changed
```

## Lifecycle

| Command | Purpose |
|---------|---------|
| `haki init` | Create `~/.haki` directories |
| `haki status` | Living modules vitality (stage, ops) |
| `haki health` | Component health (brain may be idle until weights load) |
| `haki heal` | One low-risk self-heal cycle |
| `haki daemon` | Background health + becoming + self-heal |

## Thinking (specialized brain)

| Command | Purpose |
|---------|---------|
| `haki chat` | Interactive assess→research→experiment→learn |
| `haki chat -m "..."` | One-shot question |
| `haki chat --no-experiment` | Skip Lab/experiment phase |
| `haki think "..."` | One episode + full phase trace table |
| `haki brain` | Model card: base, adapter, generation, loaded |

### Chat slash commands

| Slash | Action |
|-------|--------|
| `/brain` | Model card |
| `/mastery` | Competence map |
| `/evolve` | One Lab evolution cycle |
| `/health` | Health report |
| `/memory` | Recent memories |
| `/search <q>` | Memory search |
| `/remember <text>` | Store insight |
| `quit` / `exit` | Leave chat |

## Knowledge (Wiki)

| Command | Purpose |
|---------|---------|
| `haki wiki init` | Create wiki schema/index/log |
| `haki wiki ingest <file> -t Title -e A,B -c c1,c2` | Compile source into wiki |
| `haki wiki query "..."` | Content-aware retrieval |
| `haki wiki lint` | Orphans, stale, suggestions |
| `haki wiki status` | Page counts by type |

## Self-evolution

| Command | Purpose |
|---------|---------|
haki evolve             # foreground (blocks terminal)
haki daemon &           # start daemon with background evolve worker
haki evolve -n 3        # queues 3 cycles on daemon (non-blocking)
# check results after background run:
cat ~/.haki/lab/results.tsv
haki brain               # generation + adapter after promote

## Kaizen & becoming

```bash
haki kaizen list
haki kaizen stats
haki kaizen add -t "title" -p "problem" -a "action" -i "impact" -c defect

haki become status
haki become question
haki become propose
```

## Quiz pairs

**Q:** How do I ask one question with a phase trace?  
**A:** `haki think "your question"`

**Q:** How do I see if an adapter was promoted?  
**A:** `haki brain` — look at generation and adapter_path.

**Q:** How do I ingest a feed file?  
**A:** `haki wiki ingest feed/self/01-identity.md -t "Haki Identity" -e "Haki" -c "identity,local AI"`

**Q:** Do I rebuild after every update?  
**A:** No. With `pip install -e .`, pull and restart is enough unless dependencies changed.
