# CLI Module

Rich-based command-line interface for Haki.

## Commands

```
haki init          # Initialize directories
haki daemon        # Start daemon
haki chat          # Interactive chat
haki chat -m "hi"  # Single message
haki health        # System health report
haki lab           # Run fine-tuning
haki rag <query>   # RAG query
haki ingest <file> # Ingest document
haki status        # Quick status
```

## Chat Interactive Mode

```
┌─ Haki Chat ────────────────────────────────────────┐
│ Type 'quit' or 'exit' to stop.                    │
│ Commands: /health, /memory, /search, /remember    │
└───────────────────────────────────────────────────┘

You: Hello!
Thinking...
┌──────────────────────────────────────────┐
│ Hi there! I'm Haki, your cognitive OS.   │
│ How can I help you today?                │
└──────────────────────────────────────────┘

You: /health
┌─ Health Report ──────────────────────────┐
│ brain   │ healthy │ 0.1ms               │
│ memory  │ healthy │ 2.3ms               │
│ rag     │ healthy │ 0.5ms               │
│ disk    │ healthy │ 0.0ms               │
│ bus     │ healthy │ 0.0ms               │
└──────────────────────────────────────────┘
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/health` | Show full health report |
| `/memory` | Show recent memories |
| `/search <query>` | Semantic memory search |
| `/remember <text>` | Store a fact |
| `/quit` or `/exit` | Exit chat |

## Status Output

```bash
$ haki status
┌─ Haki Status ────────────────────────────────────┐
│ Narrow model: TinyLlama/TinyLlama-1.1B-Chat-v1.0 │
│ Wide model: gpt-4o-mini                          │
│ API configured: True                             │
│ Data dir: ~/.haki                                │
│ Lab dir: ~/.haki/lab                             │
└──────────────────────────────────────────────────┘
```

## Implementation

Built with Click (CLI framework) + Rich (terminal output).

```python
@click.group()
def cli():
    """Haki — Cognitive OS."""
    pass

@cli.command()
@click.option("--message", "-m")
@click.option("--tier", type=click.Choice(["narrow", "wide"]))
def chat(message, tier):
    """Chat with Haki's brain."""
    ...
```

## Configuration

CLI inherits all env vars from `HakiConfig`. No separate config.

## Design Decisions

1. **Rich output**: Beautiful tables, panels, syntax highlighting
2. **Click framework**: Composable commands, automatic help
3. **Sync bridge**: `asyncio.run()` wraps async module calls
4. **Interactive + scriptable**: Both REPL and one-shot commands

## Limitations

- No streaming output (waits for full response)
- No autocompletion or history
- Windows terminal colors may need `rich.console.Console` adjustment
- No progress bars for long operations (Lab training)
