# CHANGELOG

## 0.1.2 — 2026-07-13

### Added
- `haki/self_heal.py` — L2 SelfHealer cycle + `haki heal` CLI  
- Lab seed training pairs + `allow_seed` / `training_pair_count`  
- Richer memory insight patterns + user_model updates  
- Daemon self-heal loop + last meaningful change tracking  
- Docs for self-heal, refreshed architecture/API/quickstart  

### Fixed
- Pydantic Settings `ConfigDict` migration (no class Config warning)  
- Embedding dimension API compatibility  
- Lab fail-fast empty-data path without accidental training starts  
- Self-heal no longer auto-downloads large models  
- Windows-safe daemon signal registration  

### Tests
- 17 tests green (`tests/test_core.py`, `tests/test_kaizen.py`)

## 0.1.1 — 2026-07-13

### Added
- Kaizen continuous improvement log + CLI  
- Brain/Lab as Organisms  
- Wiki content-aware query scoring  
- Regression suite for CLI shadowing and lab guards  

### Fixed
- CLI `lab`/`rag` module name shadowing  
- Untracked `__pycache__` artifacts  

## 0.1.0 — 2026-07-13

### Added
- Bootstrap Cognitive OS: brain, memory, rag, lab, health, daemon, mcp, cli  
- LLM Wiki module  
- Becoming architecture (organism + philosophy)  
- Initial documentation suite  
