# Organism Module

The living base class for all Haki modules — the foundation of the becoming architecture.

## Core Idea

Every module in Haki is an organism: it has a lifecycle, metabolism, and the capacity to adapt and transform. Nothing is static — every component is a process of becoming.

## Life Cycle

```
BIRTH → GROWTH → MATURITY → TRANSFORMATION → (DORMANCY | DEATH)
```

| Stage | When | Meaning |
|-------|------|---------|
| `BIRTH` | Initialization | Just created, no operations yet |
| `GROWTH` | 3+ operations | Accumulating experience |
| `MATURITY` | 20+ operations | Stable, contributing |
| `TRANSFORMATION` | During structural change | Undergoing identity-level change |
| `DORMANCY` | Inactive but recoverable | Alive but not contributing |
| `DEATH` | End-of-life | To be replaced by new organism |

## Metabolism

Tracks the flow of energy through the organism — the sign of being alive:

```python
@dataclass
class Metabolism:
    created_at: datetime
    last_active: datetime
    operations_count: int        # How many things this organism has done
    last_operation: str          # What it just did
    total_input_bytes: int       # Information consumed
    total_output_bytes: int      # Information produced
    error_count: int             # Failures / stress

    def pulse(operation, input_bytes, output_bytes) → None
    def error() → None
    @property error_rate → float
    @property idle_seconds → float
```

A healthy metabolism has:
- Low error rate (< 5%)
- Regular activity (low idle time)
- Balanced input/output (not consuming without producing)

## API

```python
class Organism:
    def __init__(self, name: str)
    def pulse(operation, input_bytes, output_bytes) → void
    def error() → void
    def ask(question: str) → void          # External questioning
    def adapt(reason: str, change: dict) → void   # Small change
    def transform(new_structure: dict) → void      # Structural change
    def get_vitality() → dict               # Full vitality report
    def die() → void                        # End-of-life
    @property is_alive → bool
```

## Adaptations vs Transformations

**Adaptation** = small change, same identity
- Adding a new cross-link between wiki pages
- Adjusting routing thresholds in the brain
- Learning a new user preference

```python
self.adapt("new cross-link discovered", {
    "from": "entities/python.md",
    "to": "concepts/programming.md",
})
```

**Transformation** = structural change, new identity
- Changing the brain's routing architecture entirely
- Restructuring the wiki's schema
- Switching the base model

```python
self.transform({
    "routing": "learned_classifier",  # was: heuristic
    "training_data": "last_100_queries",
})
```

## Vitality Report

```python
vitality = organism.get_vitality()
# {
#     "name": "Wiki",
#     "stage": "maturity",
#     "age_seconds": 86400,
#     "operations": 156,
#     "error_rate": 0.01,
#     "adaptations": 23,
#     "transformations": 1,
#     "recent_questions": ["...", "..."]
# }
```

##死亡 (Death)

Death is not failure — it's the necessary end that makes room for new birth. In Haki:

1. An organism's stage is set to `DEATH`
2. Its knowledge is absorbed by related organisms
3. A new organism is born to replace it
4. The old one's `adaptations` and `transformations` are preserved as "ancestral knowledge"

## When Organisms Die

| Organism | Death Condition |
|----------|----------------|
| Wiki page | Stale for 60+ days, content absorbed elsewhere |
| Memory node | Importance below threshold for 30+ days |
| Model adapter | Superseded by a better adapter |
| Lab experiment | Results clearly worse than baseline |

## Integration

Every long-lived Haki module extends Organism:

```python
class Wiki(Organism): ...
class Brain(Organism): ...
class MemoryGraph(Organism): ...
class Lab(Organism): ...
class HealthMonitor(Organism): ...
class HakiDaemon(Organism): ...
class SelfHealer(Organism): ...
```

After each significant operation, call `self.pulse()`. On errors, call `self.error()`.

## CLI

```bash
haki status
# Shows vitality of ALL organisms in a table
```

## Design Decisions

1. **Everything is alive** — no passive components. Even the daemon pulses.
2. **Death is planned** — organisms have finite lifespans. Stagnation leads to death.
3. **Metabolism as health** — not just "is it running?" but "is energy flowing?"
4. **Transformation is first-class** — change is not a failure mode, it's the goal.

## Limitations

- No automatic death detection (manual call to `die()` for now)
- No reproduction (organisms don't automatically spawn offspring)
- Metabolism is coarse-grained (just byte counts, not semantic importance)
- No cross-organism metabolism (energy doesn't flow between organisms yet)
