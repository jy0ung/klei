"""
MCP Bridge — Model Context Protocol interfaces for Haki.

Exposes Haki's capabilities via MCP so external agents/clients can interact
with the cognitive OS through standardized tool interfaces.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from haki.config import config
from haki.daemon.bus import bus, Event

logger = logging.getLogger(__name__)


class MCPBridge:
    """
    MCP server bridge that exposes Haki tools to MCP-compatible clients.

    Tools exposed:
    - haki_chat: Send a message to Haki's brain
    - haki_remember: Store a memory
    - haki_recall: Search memories
    - haki_health: Get system health
    - haki_rag_query: Query the RAG pipeline
    """

    TOOLS = [
        {
            "name": "haki_chat",
            "description": "Send a message to Haki and get a response from the cognitive OS brain.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The user's message or query."},
                    "force_tier": {"type": "string", "enum": ["narrow", "wide"], "description": "Force a specific model tier."},
                },
                "required": ["message"],
            },
        },
        {
            "name": "haki_remember",
            "description": "Store a fact, preference, or insight in Haki's persistent memory.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The information to remember."},
                    "role": {"type": "string", "default": "insight", "description": "Type: user, assistant, system, insight."},
                },
                "required": ["content"],
            },
        },
        {
            "name": "haki_recall",
            "description": "Search Haki's memory for relevant information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for."},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "haki_health",
            "description": "Get Haki's current system health status.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "haki_rag_query",
            "description": "Query the RAG pipeline with retrieval-augmented generation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question to answer with context."},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "haki_lab_run",
            "description": "Run a Lab experiment to fine-tune a specialized model.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "epochs": {"type": "integer", "default": 1},
                    "model_id": {"type": "string"},
                },
            },
        },
    ]

    async def list_tools(self) -> list[dict]:
        """Return available MCP tools."""
        return self.TOOLS

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[dict]:
        """Execute an MCP tool call."""
        from haki.brain import brain, TierChoice
        from haki.memory import memory, MemoryNode
        from haki.rag import rag
        from haki.health import monitor
        from haki.lab import lab
        import uuid
        from datetime import datetime

        try:
            if name == "haki_chat":
                tier = None
                if arguments.get("force_tier") == "narrow":
                    tier = TierChoice.NARROW
                elif arguments.get("force_tier") == "wide":
                    tier = TierChoice.WIDE
                result = await brain.think(arguments["message"], force_tier=tier)
                # Also store + learn
                await memory.learn_from_interaction(arguments["message"], result.text)
                return [{"type": "text", "text": result.text}]

            elif name == "haki_remember":
                node = MemoryNode(
                    id=str(uuid.uuid4()),
                    content=arguments["content"],
                    role=arguments.get("role", "insight"),
                )
                await memory.store_memory(node)
                return [{"type": "text", "text": "Stored."}]

            elif name == "haki_recall":
                results = await memory.search(arguments["query"], top_k=arguments.get("top_k", 5))
                text = "\n".join(f"- [{r.role}] {r.content}" for r in results)
                return [{"type": "text", "text": text or "No memories found."}]

            elif name == "haki_health":
                report = await monitor.check_all()
                return [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]

            elif name == "haki_rag_query":
                result = await rag.retrieve(arguments["query"], top_k=arguments.get("top_k", 5))
                retrieved_text = "\n".join(
                    f"- [{c.get('source', '?')}] {c['text'][:200]}"
                    for c in result.retrieved_chunks
                )
                return [{"type": "text", "text": retrieved_text or "No context found."}]

            elif name == "haki_lab_run":
                result = await lab.fine_tune_model(
                    model_id=arguments.get("model_id"),
                    epochs=arguments.get("epochs", 1),
                )
                return [{"type": "text", "text": json.dumps(result.to_dict(), indent=2)}]

            else:
                return [{"type": "text", "text": f"Unknown tool: {name}"}]

        except Exception as e:
            return [{"type": "text", "text": f"Error: {e}"}]


# Singleton
mcp = MCPBridge()
