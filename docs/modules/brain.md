# Brain Module

The brain is Haki's dual-tier model orchestration layer, inspired by CognitiveOS.

## Architecture

```
Query → Brain.think()
           │
     ┌─────┴─────┐
     │ _is_simple? │
     └──┬─────┬──┘
        │     │
    NARROW   WIDE
   (local)  (remote)
        │     │
        └─────┘
           │
     BrainResponse
```

## How Routing Works

The `_is_simple_query()` heuristic classifies queries:

- **Narrow**: short queries (≤10 words) with simple keywords ("time", "hi", "status")
- **Wide**: everything else — complex reasoning, knowledge work, long inputs

Override with `force_tier=TierChoice.NARROW` or `force_tier=TierChoice.WIDE`.

## Narrow Model

- Default: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- HuggingFace Transformers, FP16 on GPU / FP32 on CPU
- Optional — if it fails to load, automatically falls back to Wide
- Good for: greetings, status checks, simple lookups

## Wide Model

- Default: OpenAI-compatible API (`gpt-4o-mini`)
- Requires `HAKI_LLM_API_KEY`
- Good for: reasoning, complex tasks, RAG-augmented generation

## Usage

```python
from haki.brain import brain, TierChoice

# Initialize
await brain.initialize()

# Auto-routed query
result = await brain.think("What's the weather?")
print(result.text)  # "The weather is..."

# Force wide model
result = await brain.think("Explain quantum computing", force_tier=TierChoice.WIDE)

# Check status
print(f"Narrow loaded: {brain.narrow_loaded}")
print(f"Wide configured: {brain.wide_configured}")
```

## Response Format

```python
@dataclass
class BrainResponse:
    text: str                    # Generated response
    tier: TierChoice             # Which tier responded
    tokens_in: int = 0           # Prompt tokens
    tokens_out: int = 0          # Completion tokens
    latency_ms: float = 0.0      # End-to-end latency
    model: str = ""              # Model identifier used
    error: str | None = None     # Error message if failed
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HAKI_NARROW_MODEL_ID` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Local model |
| `HAKI_LLM_API_KEY` | `""` | LLM API key |
| `HAKI_LLM_API_BASE` | `https://api.openai.com/v1` | API endpoint |
| `HAKI_LLM_MODEL` | `gpt-4o-mini` | Model name |

## Events Published

The brain publishes to the message bus:

| Topic | Payload |
|-------|---------|
| `brain.response` | `BrainResponse` (after each query) |

No events are subscribed to — the brain is a leaf node driven by the CLI/daemon.

## Design Decisions

1. **Dual-tier**: separates latency-sensitive simple queries from complex reasoning
2. **Graceful fallback**: if narrow fails for any reason, wide handles it
3. **Configurable**: swap models via env vars, no code changes
4. **Async**: all operations are async for compatibility with the daemon loop

## Limitations

- Heuristic routing, not learned (could be improved with a small classifier)
- Narrow model requires downloading ~2GB weights
- No streaming responses
- No tool-use / function calling yet
