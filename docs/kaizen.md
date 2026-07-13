# Kaizen — Continuous Improvement in Haki

Kaizen (改善) = continuous small improvement. Not a big redesign. Not a rewrite.

## Principles applied here

1. **Genchi Genbutsu** — go to the real code and observe defects
2. **Root cause, not patches** — fix the actual source of failure
3. **Eliminate waste** — fail fast, avoid heavy work when inputs are empty
4. **Standardize good practice** — living organisms pulse everywhere
5. **Measure** — kaizen log + vitality + health checks
6. **Compound** — every improvement is recorded so the next cycle starts higher

## This Kaizen pass (v0.1.1)

| Defect / Waste | Fix | Category |
|----------------|-----|----------|
| CLI `lab`/`rag` shadowed imports | Import as `lab_mod` / `rag_mod` | defect |
| Lab imported torch before data check | Empty-data guard first | waste |
| Wiki query ignored body text | Weighted title/tags/content scoring | flow |
| Brain/Lab not living organisms | `Brain(Organism)`, `Lab(Organism)` | standardization |
| No continuous improvement memory | `haki/kaizen.py` + CLI | measurement |

## CLI

```bash
haki kaizen list
haki kaizen stats
haki kaizen add -t "title" -p "problem" -a "action" -i "impact" -c defect
```

## How to run the next Kaizen cycle

1. Observe: use the product (`haki status`, `haki become status`, tests)
2. Find one pain: crash, waste, confusion, slow path
3. Fix the smallest root cause
4. Add a regression test
5. Record with `haki kaizen add ...`
6. Commit

Never batch 20 ideas. One verified improvement beats ten plans.

## Anti-patterns

- Big rewrite "because architecture is wrong"
- Adding modules without removing waste
- Measuring vanity metrics without user impact
- Skipping tests after a fix
