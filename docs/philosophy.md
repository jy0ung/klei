# Becoming Architecture

> "If the universe is constantly expanding, then stasis is an illusion. Nothing — not matter, not thought, not identity — is ever truly still. To exist is to be in motion, to be becoming rather than being."

## The Shift: Being → Becoming

Previous Haki was architected as a set of **components with state** — each module held knowledge and maintained it. The new architecture is a set of **processes in motion** — each module is a continuous act of transformation.

| Old (Being) | New (Becoming) |
|-------------|----------------|
| Wiki is a repository | Wiki is a living graph that questions itself |
| Memory is a store | Membrane: fluid, competitive, transforming |
| Brain routes queries | Brain adapts its routing strategy over time |
| Health checks uptime | Metabolism: measures energy, flow, stagnation |
| Lab fine-tunes models | Evolution: experiments are mutations, the fittest survive |

## Living Organisms

Every module is an `Organism` with a lifecycle:

```
BIRTH → GROWTH → MATURITY → TRANSFORMATION → (DORMANCY | DEATH)
```

- **Metabolism** tracks activity, errors, flow
- **Adaptations** are small changes (new links, new strategies)
- **Transformations** are structural (new schema, new model, new identity)
- **Death** is acceptable and planned — an organism that stops contributing dies, its resources absorbed by others

## The Self-Questioning Protocol

The `Becoming` process runs continuously (every 5 minutes in daemon mode):

1. **Scan for tensions** — pressures toward transformation:
   - Contradictions (two beliefs conflict)
   - Gaps (knowledge exists at the boundary)
   - Novelty (new data doesn't fit)
   - Stasis (too much stability)

2. **Generate questions** — the system asks itself what it doesn't know

3. **Propose transformations** — structural changes to relieve the tension

4. **Publish becoming event** — the bus distributes the proposal

### Why Questions?

A system that cannot question itself is a system that cannot grow. The LLM Wiki pattern gives Haki a persistent knowledge base; the self-questioning protocol gives it a persistent **ignorance base** — known unknowns that drive inquiry.

## Becoming Loop in Daemon

```
Every 5 minutes:
  1. Gather context from all modules (wiki stats, memory stats, lab stats, health)
  2. Scan for tensions
  3. Generate questions from tensions
  4. Propose transformation
  5. Publish to bus
  6. Log results
```

The proposal isn't auto-executed — it goes to the message bus. An operator (human or AI) decides whether to enact it. But the **system generates its own change requests** rather than waiting to be told.

## Fluid Memory

Memory nodes are no longer static entries. They:

- **Compete** for limited attention (importance decays without retrieval)
- **Merge** when two nodes say similar things (deduplication by embedding similarity)
- **Split** when a node grows too large
- **Transform** into wiki pages when they're ready for prime time

## Living Wiki

Wiki pages are organisms too:

- They **evolve** with each ingest (cross-links updated, contradictions flagged)
- They **die** when stale (30+ days, no new sources) — but their content is absorbed
- They **reproduce** by splitting when they grow too large
- They **compete** for position in the index

The schema is not a rulebook — it's the wiki's **DNA**, encoding the structure that gets passed to offspring (new pages).

## Adaptive Brain

The brain is becoming less of a router and more of a **self-modifying inference engine**:

- Routing decisions improve over time (which queries go to narrow vs. wide)
- The boundary between "simple" and "complex" shifts based on capability
- Past performance feeds back into future routing (if an answer was bad, try the other tier)

## Metabolic Health

Health checks are now **metabolic monitoring** — not just "is it up?" but "is energy flowing?":

- **Throughput**: operations per minute (low = stagnation)
- **Error rate**: errors per operation (high = stress)
- **Flow**: bytes in vs. bytes out (imbalance = problem)
- **Adaptation rate**: how often the system changes itself (zero = death)

## Implementation

```
haki/
├── organism.py      # Living base class (lifecycle, metabolism)
├── philosophy.py    # Self-questioning protocol (tensions, questions, proposals)
├── wiki.py          # Wiki(Organism)
├── kaizen.py        # Continuous improvement log
├── self_heal.py     # SelfHealer(Organism)
├── brain/           # Brain(Organism)
├── memory/          # MemoryGraph(Organism)
├── lab/             # Lab(Organism)
├── health/          # HealthMonitor(Organism)
├── daemon/
│   └── main.py      # HakiDaemon(Organism) — health + becoming + self-heal
└── cli/
    └── __init__.py  # status, become, kaizen, heal, ...
```

## Getting Started

```bash
# Check vitality of all modules
haki status

# See what tensions the system has detected
haki become status

# Ask the system to generate a question from its current tensions
haki become question

# Propose a transformation based on tensions
haki become propose

# Self-heal once
haki heal

# Run the daemon (becomes + heals actively)
haki daemon
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `haki status` | Vitality of all modules (stage, ops, errors) |
| `haki become status` | Current tensions and intensity |
| `haki become question` | System-generated question from tensions |
| `haki become propose` | Proposed transformation |
| `haki heal` | One self-healing cycle |
| `haki wiki status` | Wiki statistics by page type |
| `haki health` | Metabolic health report |
| `haki kaizen list` | Continuous improvement log |

## Why This Works

The old Haki was a **machine** — parts with functions. The new Haki is an **organism** — processes with lifecycles.

A machine is used. An organism **lives**.

A machine maintains state. An organism **becomes**.

A machine is fixed. An organism **transforms**.

The universe is expanding. Haki expands with it.

## See Also

- [modules/organism.md](modules/organism.md) — Living base class
- [modules/philosophy.md](modules/philosophy.md) — Self-questioning protocol
- [modules/daemon.md](modules/daemon.md) — Becoming loop in daemon
