"""
RAG Pipeline — Retrieval-Augmented Generation.

Based on AWS RAG pattern: retrieve relevant context from knowledge sources,
then augment LLM prompts with retrieved information.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from haki.config import config
from haki.memory import MemoryGraph, MemoryNode

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    query: str
    retrieved_chunks: list[dict[str, Any]] = field(default_factory=list)
    augmented_prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Combines:
    1. Memory graph search (episodic/conversational memory)
    2. Document index (static knowledge)
    3. Web search results (dynamic knowledge)

    Produces augmented prompts for the brain.
    """

    def __init__(self, memory: MemoryGraph | None = None):
        self.memory = memory or MemoryGraph()
        self._documents: list[dict[str, Any]] = []
        self._doc_index_path = Path(str(config.memory_db) + ".docs.faiss")
        self._doc_index = None
        self._doc_texts: list[str] = []

    async def initialize(self) -> None:
        """Load document index if available."""
        try:
            import faiss
            import numpy as np
            if self._doc_index_path.exists():
                self._doc_index = faiss.read_index(str(self._doc_index_path))
                # Load doc texts from sidecar
                sidecar = Path(str(self._doc_index_path) + ".json")
                if sidecar.exists():
                    import json
                    self._doc_texts = json.loads(sidecar.read_text())
                logger.info("RAG document index loaded with %d chunks.", self._doc_index.ntotal)
        except Exception as e:
            logger.warning("RAG doc index load failed: %s", e)

    async def add_document(self, text: str, source: str = "unknown", metadata: dict | None = None) -> None:
        """Add a document to the RAG index."""
        chunks = self._chunk_text(text)
        if not chunks:
            return

        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(config.embedding_model)
            embeddings = model.encode(chunks)
            faiss.normalize_L2(embeddings.astype(np.float32))

            if self._doc_index is None:
                dim = embeddings.shape[1]
                self._doc_index = faiss.IndexFlatIP(dim)

            self._doc_index.add(embeddings.astype(np.float32))
            self._doc_texts.extend(chunks)

            # Persist
            faiss.write_index(self._doc_index, str(self._doc_index_path))
            sidecar = Path(str(self._doc_index_path) + ".json")
            sidecar.write_text(json.dumps(self._doc_texts))

            logger.info("Added %d chunks from source=%s", len(chunks), source)
        except Exception as e:
            logger.error("Failed to add document: %s", e)

    async def retrieve(self, query: str, top_k: int | None = None) -> RAGResult:
        """
        Retrieve relevant context from all sources and build augmented prompt.
        """
        top_k = top_k or config.rag_top_k
        result = RAGResult(query=query)
        chunks: list[dict[str, Any]] = []

        # 1. Memory graph search
        try:
            memory_nodes = await self.memory.search(query, top_k=top_k)
            for node in memory_nodes:
                chunks.append({
                    "text": node.content,
                    "source": "memory",
                    "role": node.role,
                    "score": node.importance,
                })
        except Exception as e:
            logger.warning("Memory search failed: %s", e)

        # 2. Document index search
        if self._doc_index is not None and self._doc_index.ntotal > 0:
            try:
                import numpy as np
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(config.embedding_model)
                vec = model.encode([query])
                faiss.normalize_L2(vec.astype(np.float32))
                scores, indices = self._doc_index.search(vec.astype(np.float32), top_k)
                for idx, score in zip(indices[0], scores[0]):
                    if idx >= 0 and idx < len(self._doc_texts):
                        chunks.append({
                            "text": self._doc_texts[idx],
                            "source": "document",
                            "score": float(score),
                        })
            except Exception as e:
                logger.warning("Doc search failed: %s", e)

        # Sort by score and take top_k
        chunks.sort(key=lambda c: c.get("score", 0), reverse=True)
        result.retrieved_chunks = chunks[:top_k]
        result.augmented_prompt = self._build_augmented_prompt(query, result.retrieved_chunks)
        return result

    def _build_augmented_prompt(self, query: str, chunks: list[dict[str, Any]]) -> str:
        """Build augmented prompt with retrieved context."""
        if not chunks:
            return query

        context_parts = []
        for i, chunk in enumerate(chunks):
            source = chunk.get("source", "unknown")
            text = chunk["text"]
            context_parts.append(f"[Context {i+1} from {source}]: {text}")

        context_block = "\n\n".join(context_parts)
        augmented = f"""Based on the following context, answer the user's question accurately.

Context:
{context_block}

User question: {query}

Answer (citing sources where applicable):"""
        return augmented

    def _chunk_text(self, text: str, chunk_size: int | None = None, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or config.rag_chunk_size
        words = text.split()
        if len(words) <= chunk_size:
            return [text.strip()]
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks


# Singleton
rag = RAGPipeline()
