# Contributing

## Dev Setup

```bash
git clone https://github.com/jy0ung/klei.git
cd klei

# Create venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev deps
pip install -e ".[dev]"
```

## Project Structure

```
klei/
├── haki/
│   ├── brain/       # Dual-tier model orchestration
│   ├── memory/      # Persistent self-learning memory
│   ├── rag/         # Retrieval-augmented generation
│   ├── lab/         # Autonomous model creation
│   ├── health/      # Self-healing monitor
│   ├── daemon/      # Message bus + main loop
│   ├── mcp/         # MCP bridge
│   ├── cli/         # Command-line interface
│   ├── config.py    # Global config (Pydantic)
│   └── __init__.py
├── tests/
│   └── test_core.py
├── docs/            # Sphinx/mkdocs (future)
├── pyproject.toml
└── README.md
```

## Conventions

### Code Style

- Python 3.10+
- Line length: 100
- Formatter: `ruff format`
- Linter: `ruff check`
- Type hints on all public functions
- Async-first: `async def` for any I/O

```bash
# Lint
ruff check haki/

# Format
ruff format haki/
```

### Module Structure

Each module follows:

```
haki/<module>/
└── __init__.py     # Public API + singleton instance
```

- Export a module-level singleton (e.g., `brain = Brain()`)
- Keep implementation in `__init__.py` for modules < 500 LOC
- Split into sub-files when exceeding 500 LOC

### Naming

- `PascalCase` for classes
- `snake_case` for functions/variables
- `UPPER_SNAKE` for constants
- Prefix event topics with `haki.`

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=haki --cov-report=term-missing
```

Tests must:
- Use `pytest-asyncio` for async tests
- Use `tmp_path` for file fixtures
- Mock external API calls (LLM endpoints)
- Not require GPU — skip with `@pytest.mark.skipif(not torch.cuda.is_available())`

### Commit Messages

```
type(short): description

- detail
- detail
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Adding a New Module

1. Create `haki/<module>/__init__.py`
2. Define singleton class with `async def initialize()`
3. Register in `daemon/main.py` startup
4. Add MCP tools (if applicable) in `mcp/__init__.py`
5. Add CLI commands (if applicable) in `cli/__init__.py`
6. Write tests in `tests/test_<module>.py`
7. Document in `docs/modules/<module>.md`

## Release Process

1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` (future)
3. Tag: `git tag v0.x.x`
4. Push: `git push origin main --tags`
5. (Future) Build + publish to PyPI

## Code of Conduct

- Be constructive in reviews
- No AI-generated toxicity
- Credit sources when borrowing code

## License

MIT
