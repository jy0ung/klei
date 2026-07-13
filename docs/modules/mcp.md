# MCP Bridge Module

Model Context Protocol interface for Haki — exposes cognitive OS capabilities to any MCP client.

## Overview

```
MCP Client (Claude Code, etc.)
          │
          │  MCP protocol
          ↓
    ┌───────────┐
    │ MCP Bridge │
    └───────────┘
          │
          ↓
    Haki tools (brain, memory, RAG, lab, health)
```

## Exposed Tools

| Tool | Input | Output |
|------|-------|--------|
| `haki_chat` | `message`, `force_tier?` | Response text |
| `haki_remember` | `content`, `role?` | Confirmation |
| `haki_recall` | `query`, `top_k?` | List of memories |
| `haki_health` | `{}` | Full health report |
| `haki_rag_query` | `query`, `top_k?` | Retrieved chunks |
| `haki_lab_run` | `epochs?`, `model_id?` | Experiment result |

## Tool Definitions

```json
{
  "name": "haki_chat",
  "description": "Send a message to Haki and get a response.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {"type": "string"},
      "force_tier": {"type": "string", "enum": ["narrow", "wide"]}
    },
    "required": ["message"]
  }
}
```

## Usage (Python)

```python
from haki.mcp import mcp

# List available tools
tools = await mcp.list_tools()

# Call a tool
result = await mcp.call_tool("haki_chat", {"message": "Hello!"})
# result = [{"type": "text", "text": "Hi there!..."}]
```

## Usage (Any MCP Client)

Start the daemon with MCP bridge:

```bash
haki daemon
```

Then connect any MCP-compatible client to `http://localhost:8765` (future).

## Implementation

The bridge maps MCP tool calls to internal Python coroutines:

```python
async def call_tool(self, name: str, arguments: dict) -> list[dict]:
    if name == "haki_chat":
        result = await brain.think(arguments["message"])
        return [{"type": "text", "text": result.text}]
    elif name == "haki_remember":
        # ...
    # etc
```

## Error Handling

Errors are returned as text responses, not protocol errors:

```python
try:
    result = await brain.think(...)
except Exception as e:
    return [{"type": "text", "text": f"Error: {e}"}]
```

## Security

- No auth on bridge (localhost only in current impl)
- No rate limiting
- Input validation via Pydantic Schemas

## Future

- SSE/stdio MCP transport
- Streaming responses for chat
- Tool result caching
- Per-tool rate limits
