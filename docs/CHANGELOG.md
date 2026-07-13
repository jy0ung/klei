# CHANGELOG

## 0.2.0 — local-only self-evolving brain

### Breaking
- **Removed cloud LLM API** as product brain (`HAKI_LLM_API_*` gone)
- Dual-tier narrow/wide routing removed

### Added
- Default base: `HuggingFaceTB/SmolLM2-360M-Instruct` (~4GB-class)
- `active_model.json` + `brain.promote_adapter()` / `reload()`
- `Lab.evolve_once` / `evolve_loop` with auto-promote on better val_bpb
- CLI: `haki evolve`, `haki brain`
- Rule-based local fallback when weights not loaded
- Architecture docs rewritten for self-evolution loop

### Changed
- Lab defaults CPU-friendly (`lab_gpu=false`)
- Health brain check reports local generation

## 0.1.2

Self-heal, richer insights, Lab seed pairs, ConfigDict, embedding compat.

## 0.1.1 / 0.1.0

Kaizen, becoming, wiki, bootstrap Cognitive OS.
