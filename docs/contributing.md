# Contributing

## Dev Setup

```bash
git clone https://github.com/jy0ung/klei.git
cd klei
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

## Project Structure

```
klei/
├── haki/
│   ├── brain/ memory/ rag/ lab/ health/ daemon/ mcp/ cli/
│   ├── wiki.py organism.py philosophy.py kaizen.py self_heal.py config.py
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Conventions

- Python 3.10+, async-first for I/O  
- Line length 100 (ruff)  
- Prefer `Organism` subclass for long-lived modules  
- Call `pulse()` / `error()` on real operations  
- CLI command names must not shadow imported modules (`lab_mod` pattern)  
- Self-heal must stay low-risk (no surprise downloads)  

## Testing

```bash
pytest tests/ -v
pytest tests/test_kaizen.py -v
```

Add a regression test with every defect fix.

## Kaizen (required for non-trivial fixes)

```bash
haki kaizen add \
  -t "short title" \
  -p "what was wrong" \
  -a "what you changed" \
  -i "user-visible impact" \
  -c defect   # or waste|flow|standardization|measurement
```

Process: observe → one root cause → fix → test → record → commit.

## Commit Style

```
type(scope): summary

Types: feat, fix, docs, refactor, test, chore
```

## Docs

Update docs when behavior changes:

- `README.md` + `docs/README.md` for entry points  
- `docs/api.md` for public APIs  
- Module page under `docs/modules/`  
- `docs/CHANGELOG.md` for releases  

## License

MIT
