# CHANGELOG

## 0.2.0 — local-only self-evolving brain

### Breaking
- **Removed cloud LLM API** as the product brain
- Dual-tier narrow/wide routing removed; single **local** brain

### Added
- Default base: `HuggingFaceTB/SmolLM2-360M-Instruct` (~4GB-friendly)
- `active_model.json` + `brain.promote_adapter()` self-replacement
- `Lab.evolve_once` / `evolve_loop` with auto-promote on better val_bpb
- CLI: `haki evolve`, `haki brain`
- Rule-based local fallback when weights not loaded

### Changed
- Lab defaults CPU-friendly (`lab_gpu=false`)
- Health brain check reports local generation

## 0.1.2 and earlier

See prior commits for self-heal, wiki, becoming, kaizen bootstrap.
