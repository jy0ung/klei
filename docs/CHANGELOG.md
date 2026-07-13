# CHANGELOG

## 0.3.0 — specialized thinking brain

### Added
- `haki/cognition.py` — SpecializedBrain: assess → research → experiment → synthesize → learn
- `haki/mastery.py` — durable competence map (`mastery.json`)
- CLI: `haki think`, `haki mastery`; chat uses specialized loop
- Docs: `docs/modules/cognition.md`

### Behavior
- Unknown → memory/wiki/RAG research
- Still weak → experiment (hypothesis + Lab evolve for self-improve queries)
- Continuous mastery updates after every episode

## 0.2.0 — local-only self-evolving brain

### Breaking
- **Removed cloud LLM API** as product brain
- Dual-tier narrow/wide routing removed

### Added
- SmolLM2-360M default, promote LoRA into living brain
- `haki evolve`, `haki brain`

### Changed
- Lab defaults CPU-friendly (`lab_gpu=false`)
- Health brain check reports local generation

## 0.1.2

Self-heal, richer insights, Lab seed pairs, ConfigDict, embedding compat.

## 0.1.1 / 0.1.0

Kaizen, becoming, wiki, bootstrap Cognitive OS.
