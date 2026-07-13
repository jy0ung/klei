"""
Memory graph — persistent, self-learning memory system.

Inspired by Honcho's Architecture:
- Stores all interactions in a peer-centric graph
- Continuously analyzes conversations to build user models (Theory of Mind)
- Provides retrieval APIs for RAG and context windows

Backend: SQLite + FAISS for vector search.

Note: The Wiki module (wiki.py) is the primary knowledge interface.
This memory graph persists as the backend store and real-time event capture layer.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from haki.config import config
from haki.organism import Organism

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.utcnow()


def _embedding_dim(model) -> int:
    """Compat: sentence-transformers renamed get_sentence_embedding_dimension."""
    if hasattr(model, "get_embedding_dimension"):
        return int(model.get_embedding_dimension())
    if hasattr(model, "get_sentence_embedding_dimension"):
        return int(model.get_sentence_embedding_dimension())
    # last resort: encode a probe
    vec = model.encode(["probe"])
    return int(len(vec[0]))


@dataclass
class MemoryNode:
    """A single memory entry — a conversation turn, fact, or insight."""
    id: str
    content: str
    role: str  # "user", "assistant", "system", "insight"
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)
    importance: float = 1.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "importance": self.importance,
        }


class MemoryGraph(Organism):
    """
    Persistent memory graph that learns from every interaction.

    - Stores messages + generated insights (Theory of Mind)
    - Vector search for retrieval
    - Self-reinforcing: updates user model on each interaction
    """

    def __init__(self):
        super().__init__("Memory")
        self._db_path = config.memory_db
        self._index_path = Path(str(config.memory_db) + ".faiss")
        self._embedding_model = None
        self._index = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load DB, embedding model, and index."""
        if self._initialized:
            return

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        await self._init_sqlite()
        await self._init_embedding_model()
        await self._init_index()
        self._initialized = True
        self.pulse("initialized")
        logger.info("Memory graph initialized with %d nodes.", len(await self.get_all()))

    async def _init_sqlite(self) -> None:
        """Initialize SQLite schema."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    role TEXT NOT NULL,
                    embedding BLOB,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    importance REAL DEFAULT 1.0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_model (
                    id INTEGER PRIMARY KEY,
                    theory_of_mind TEXT,
                    preferences TEXT,
                    communication_style TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT,
                    assistant_output TEXT,
                    tier_used TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def _init_embedding_model(self) -> None:
        """Load sentence-transformer embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(config.embedding_model)
            logger.info("Embedding model loaded: %s", config.embedding_model)
        except Exception as e:
            logger.warning("Could not load embedding model: %s", e)
            self._embedding_model = None

    async def _init_index(self) -> None:
        """Initialize FAISS index for vector search."""
        if self._embedding_model is None:
            return
        try:
            import faiss
            dim = _embedding_dim(self._embedding_model)
            if self._index_path.exists():
                self._index = faiss.read_index(str(self._index_path))
            else:
                self._index = faiss.IndexFlatIP(dim)  # inner product (cosine for normalized)
        except Exception as e:
            logger.warning("FAISS init failed: %s", e)

    async def store_memory(self, node: MemoryNode) -> None:
        """Store a memory node (with optional embedding)."""
        import aiosqlite
        # Generate embedding
        if self._embedding_model and node.content.strip():
            node.embedding = self._embedding_model.encode(node.content).tolist()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """INSERT INTO memories (id, content, role, embedding, metadata, importance)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    node.id,
                    node.content,
                    node.role,
                    json.dumps(node.embedding) if node.embedding else None,
                    json.dumps(node.metadata),
                    node.importance,
                ),
            )
            await db.commit()

        # Update index
        if self._index is not None and node.embedding:
            import numpy as np
            import faiss
            vec = np.array([node.embedding], dtype=np.float32)
            faiss.normalize_L2(vec)
            self._index.add(vec)
            faiss.write_index(self._index, str(self._index_path))
        self.pulse("store_memory", input_bytes=len(node.content))

    async def store_interaction(self, user_input: str, assistant_output: str, tier: str = "") -> None:
        """Log an interaction (for self-learning)."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO interactions (user_input, assistant_output, tier_used) VALUES (?, ?, ?)",
                (user_input, assistant_output, tier),
            )
            await db.commit()
        self.pulse("store_interaction", input_bytes=len(user_input) + len(assistant_output))

    async def search(self, query: str, top_k: int | None = None) -> list[MemoryNode]:
        """Search memories by semantic similarity."""
        if self._embedding_model is None or self._index is None or self._index.ntotal == 0:
            results = await self._text_search(query, top_k)
            self.pulse("search_text", input_bytes=len(query))
            return results

        import numpy as np
        import faiss
        top_k = top_k or config.rag_top_k
        vec = self._embedding_model.encode([query])
        faiss.normalize_L2(vec.astype(np.float32))
        scores, indices = self._index.search(vec.astype(np.float32), top_k)

        # Map indices back to nodes (we store in insertion order)
        all_nodes = await self.get_all()
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx >= 0 and idx < len(all_nodes):
                all_nodes[idx].importance *= (1 + float(score))  # reinforce
                results.append(all_nodes[idx])
        self.pulse("search", input_bytes=len(query), output_bytes=len(results))
        return results

    async def _text_search(self, query: str, top_k: int | None = None) -> list[MemoryNode]:
        """Fallback: substring search when embeddings unavailable."""
        import aiosqlite
        top_k = top_k or config.rag_top_k
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC, created_at DESC LIMIT 10",
                (f"%{query}%",),
            )
            rows = await cursor.fetchall()
        return [
            MemoryNode(
                id=r["id"], content=r["content"], role=r["role"],
                importance=r["importance"],
            )
            for r in rows
        ]

    async def get_all(self) -> list[MemoryNode]:
        """Get all memories (ordered by id/insertion)."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM memories ORDER BY created_at ASC"
            )
            rows = await cursor.fetchall()
        return [
            MemoryNode(
                id=r["id"], content=r["content"], role=r["role"],
                importance=r["importance"], created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    async def update_user_model(self, theory_of_mind: str, preferences: dict, comm_style: str) -> None:
        """Update the Theory of Mind model from accumulated interactions."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("DELETE FROM user_model")  # single-row table
            await db.execute(
                """INSERT INTO user_model (theory_of_mind, preferences, communication_style, last_updated)
                   VALUES (?, ?, ?, ?)""",
                (theory_of_mind, json.dumps(preferences), comm_style, datetime.utcnow()),
            )
            await db.commit()

    async def get_user_model(self) -> dict[str, Any] | None:
        """Retrieve the current user model."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM user_model")
            row = await cursor.fetchone()
        if row:
            return {
                "theory_of_mind": row["theory_of_mind"],
                "preferences": json.loads(row["preferences"] or "{}"),
                "communication_style": row["communication_style"],
                "last_updated": row["last_updated"],
            }
        return None

    async def get_recent_interactions(self, n: int = 20) -> list[dict]:
        """Get recent interactions for context window."""
        import aiosqlite
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM interactions ORDER BY timestamp DESC LIMIT ?", (n,)
            )
            rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def learn_from_interaction(self, user_input: str, assistant_output: str) -> None:
        """
        Self-learning: analyze interaction and update memory + user model.
        Called after each response to accumulate understanding.
        """
        # Store raw interaction
        await self.store_interaction(user_input, assistant_output)

        # Generate insights about user
        insights = self._extract_insights(user_input, assistant_output)
        for insight in insights:
            node = MemoryNode(
                id=f"insight-{_utc_now().isoformat()}-{hash(insight) % 10000}",
                content=insight,
                role="insight",
                importance=0.8,
            )
            await self.store_memory(node)

        # Update lightweight user model from cumulative insights
        if insights:
            model = await self.get_user_model() or {
                "theory_of_mind": "",
                "preferences": {},
                "communication_style": "unknown",
            }
            prefs = model.get("preferences") or {}
            for insight in insights:
                if insight.startswith("User preference:"):
                    prefs["likes"] = prefs.get("likes", []) + [insight]
                elif insight.startswith("User dislike:"):
                    prefs["dislikes"] = prefs.get("dislikes", []) + [insight]
                elif insight.startswith("User name:"):
                    prefs["name"] = insight.split(":", 1)[-1].strip()
                elif insight.startswith("User goal:"):
                    prefs["goals"] = prefs.get("goals", []) + [insight]
            tom = model.get("theory_of_mind") or ""
            if insights:
                tom = (tom + " | " + " ; ".join(insights[-3:])).strip(" |")
            await self.update_user_model(
                theory_of_mind=tom[:2000],
                preferences=prefs,
                comm_style=model.get("communication_style") or "unknown",
            )
        self.pulse("learn_from_interaction", input_bytes=len(user_input))

    def _extract_insights(self, user_input: str, assistant_output: str) -> list[str]:
        """
        Structured insight extraction beyond single-phrase regex.
        Uses multiple pattern families; LLM-based extraction can replace this later.
        """
        import re

        insights: list[str] = []
        text = user_input.strip()
        q = text.lower()

        patterns = [
            (r"(?:i (?:really )?like|i prefer|i love)\s+(.+)", "User preference"),
            (r"(?:i (?:really )?hate|i don't like|i dislike|i can't stand)\s+(.+)", "User dislike"),
            (r"(?:my name is|i am|i'm)\s+([A-Za-z][\w\-']{1,40})", "User name"),
            (r"(?:please always|always)\s+(.+)", "User instruction"),
            (r"(?:never|do not|don't)\s+(.+)", "User constraint"),
            (r"(?:my goal is|i want to|i need to|i'm trying to)\s+(.+)", "User goal"),
            (r"(?:i work (?:at|for)|i'm at|i am at)\s+(.+)", "User workplace"),
            (r"(?:call me|refer to me as)\s+(.+)", "User name"),
            (r"(?:timezone|i am in|i'm in)\s+([A-Za-z/_\- ]{2,40})", "User location"),
        ]

        for pattern, label in patterns:
            m = re.search(pattern, q, flags=re.IGNORECASE)
            if m:
                value = m.group(1).strip(" .,!?:;")
                if value:
                    # Preserve original casing slice when possible
                    insights.append(f"{label}: {value}")

        # Topic signal from question style
        if q.endswith("?") and len(q.split()) >= 4:
            insights.append(f"User asked about: {text[:120]}")

        # Style preference from explicit requests
        if any(w in q for w in ("be concise", "short answer", "briefly", "tl;dr")):
            insights.append("User communication style: concise")
        if any(w in q for w in ("explain in detail", "be thorough", "step by step", "deep dive")):
            insights.append("User communication style: detailed")

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for item in insights:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique


# Singleton
memory = MemoryGraph()
