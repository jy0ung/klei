# Haki Commands

Primary CLI entrypoints for self-operation and self-improvement.

## Lifecycle

```bash
haki init          # Create data directories under ~/.haki
haki status        # Organism vitality table
haki health        # Component health (local-only brain may be idle until weights load)
haki heal          # One low-risk self-heal cycle
haki daemon        # Background health + becoming + self-heal loops
```

## Thinking

```bash
haki chat                    # Specialized brain chat (assess → research → experiment → learn)
haki chat -m "question"      # One-shot
haki chat --no-experiment    # Research/synthesize only (no Lab)
haki think "question"        # One episode + full phase trace
haki brain                   # Model card: base, adapter, generation, loaded
```

### Chat slash commands

| Command | Action |
|---------|--------|
| `/brain` | Model card |
| `/mastery` | Competence map summary |
| `/evolve` | One Lab evolution cycle |
| `/health` | Health report |
| `/memory` | Recent memories |
| `/search <q>` | Memory search |
| `/remember <text>` | Store an insight |

## Knowledge (Wiki)

```bash
haki wiki init
haki wiki ingest <file.md> -t "Title" -e "Entity1,Entity2" -c "concept1,concept2"
haki wiki query "question"
haki wiki lint
haki wiki status
```

## Self-evolution (Lab)

```bash
haki evolve              # One fine-tune + promote-if-best
haki evolve -n 3 -e 1    # Multiple cycles
haki lab --epochs 1      # Explicit lab run
haki mastery             # What I know / open gaps
```

## Continuous improvement

```bash
haki kaizen list
haki kaizen stats
haki kaizen add -t "title" -p "problem" -a "action" -i "impact" -c defect
```

## Becoming

```bash
haki become status
haki become question
haki become propose
```

## Install note

Editable install (recommended): `pip install -e .`  
Code updates after `git pull` usually need **no rebuild** — only reinstall if dependencies change.
