"""
Specialized thinking brain for Haki — metacognitive control loop.

Philosophy:
  If it doesn't know what or how → research.
  If research is insufficient → experiment.
  Continuously improve until it masters itself.

This is NOT a cloud LLM agent. Control is deterministic code (reliable on tiny models).
Generation may use the local model; knowing/research/experiment is structural.

Loop:
  1. ASSESS  — do I know this? (mastery + memory + wiki signals)
  2. RESEARCH — memory search, wiki query, RAG
  3. EXPERIMENT — lab evolve / structured trial when still unknown
  4. SYNTHESIZE — answer from evidence (+ local model polish if loaded)
  5. LEARN — update mastery, memory, open questions
"""
from __future__ import annotations

import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from haki.organism import Organism

logger = logging.getLogger(__name__)


class Phase(str, Enum):
    ASSESS = "assess"
    RESEARCH = "research"
    EXPERIMENT = "experiment"
    SYNTHESIZE = "synthesize"
    LEARN = "learn"


@dataclass
class ThoughtTrace:
    """Audit trail of one cognitive episode."""
    query: str
    phases: list[str] = field(default_factory=list)
    known: bool = False
    confidence: float = 0.0
    topics: list[str] = field(default_factory=list)
    research_hits: int = 0
    experimented: bool = False
    experiment_ok: bool = False
    answer: str = ""
    sources: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    generation: int = 0
    model: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "phases": self.phases,
            "known": self.known,
            "confidence": self.confidence,
            "topics": self.topics,
            "research_hits": self.research_hits,
            "experimented": self.experimented,
            "experiment_ok": self.experiment_ok,
            "answer": self.answer[:500],
            "sources": self.sources,
            "latency_ms": self.latency_ms,
            "generation": self.generation,
            "model": self.model,
        }


# Confidence threshold: above this we answer without forced experiment
KNOW_THRESHOLD = 0.55
# Below this after research → run experiment path
EXPERIMENT_THRESHOLD = 0.40


class SpecializedBrain(Organism):
    """
    Haki's specialized brain: think-for-itself control loop.

    Uses local Brain for neural generation when available;
    never requires cloud API.
    """

    def __init__(self) -> None:
        super().__init__("SpecializedBrain")
        self._initialized = False
        self._traces: list[ThoughtTrace] = []

    async def initialize(self) -> None:
        if self._initialized:
            return
        from haki.mastery import mastery
        from haki.memory import memory
        from haki.brain import brain

        mastery.load()
        await memory.initialize()
        # Do not force-download neural weights here — structural cognition works offline.
        # Neural polish loads lazily on first synthesize if already loaded elsewhere.
        if not brain._initialized:
            brain._initialized = True  # allow model_card / fallback without download
        self._initialized = True
        self.pulse("initialized")

    async def think(self, query: str, allow_experiment: bool = True) -> ThoughtTrace:
        """
        Full metacognitive episode.

        allow_experiment=False skips Lab (fast path for tests / chat without train).
        """
        start = time.perf_counter()
        trace = ThoughtTrace(query=query)
        if not self._initialized:
            await self.initialize()

        # --- 1. ASSESS ---
        trace.phases.append(Phase.ASSESS.value)
        conf, topics = await self._assess(query)
        trace.confidence = conf
        trace.topics = [t.id for t in topics]
        trace.known = conf >= KNOW_THRESHOLD

        research_bits: list[str] = []
        sources: list[str] = []

        # --- 2. RESEARCH if not confident ---
        if not trace.known:
            trace.phases.append(Phase.RESEARCH.value)
            research_bits, sources = await self._research(query)
            trace.research_hits = len(research_bits)
            # Boost confidence if research found substance
            if research_bits:
                conf = min(1.0, conf + 0.15 * min(3, len(research_bits)))
                trace.confidence = conf
                if conf >= KNOW_THRESHOLD:
                    trace.known = True

        # --- 3. EXPERIMENT if still weak ---
        if allow_experiment and conf < EXPERIMENT_THRESHOLD:
            trace.phases.append(Phase.EXPERIMENT.value)
            ok, exp_note = await self._experiment(query, topics)
            trace.experimented = True
            trace.experiment_ok = ok
            if exp_note:
                research_bits.append(exp_note)
                sources.append("experiment")
            if ok:
                conf = min(1.0, conf + 0.12)
                trace.confidence = conf

        # --- 4. SYNTHESIZE ---
        trace.phases.append(Phase.SYNTHESIZE.value)
        answer, model_label, gen = await self._synthesize(query, research_bits, conf, trace)
        trace.answer = answer
        trace.model = model_label
        trace.generation = gen
        trace.sources = sources

        # --- 5. LEARN ---
        trace.phases.append(Phase.LEARN.value)
        await self._learn(query, answer, conf, topics, trace)

        trace.latency_ms = (time.perf_counter() - start) * 1000
        self._traces.append(trace)
        self._traces = self._traces[-100:]
        self.pulse("think", input_bytes=len(query), output_bytes=len(answer))
        return trace

    async def _assess(self, query: str) -> tuple[float, list]:
        from haki.mastery import mastery

        conf, topics = mastery.confidence_for_query(query)
        # Builtin self-knowledge boosts
        q = query.lower()
        if any(k in q for k in ("who are you", "what are you", "what is haki", "how do you")):
            conf = max(conf, 0.75)
            topics = topics or [mastery.upsert_topic("Self", "self")]
        if any(k in q for k in ("evolve", "lab", "fine-tune", "lora", "val_bpb")):
            conf = max(conf, 0.5)
            mastery.upsert_topic("Lab evolve", "lab-evolve")
        return conf, topics

    async def _research(self, query: str) -> tuple[list[str], list[str]]:
        bits: list[str] = []
        sources: list[str] = []

        # Memory
        try:
            from haki.memory import memory
            hits = await memory.search(query, top_k=5)
            for h in hits:
                bits.append(f"[memory/{h.role}] {h.content[:300]}")
                sources.append(f"memory:{h.id}")
        except Exception as e:
            logger.debug("memory research: %s", e)

        # Wiki
        try:
            from haki.wiki import wiki
            await wiki.initialize()
            wq = await wiki.query(query, top_k=3)
            if wq.get("context") and "No pages" not in wq["context"] and "No relevant" not in wq["context"]:
                bits.append(f"[wiki] {wq['context'][:800]}")
                for s in wq.get("sources") or []:
                    sources.append(f"wiki:{s.get('title', '?')}")
        except Exception as e:
            logger.debug("wiki research: %s", e)

        # RAG
        try:
            from haki.rag import rag
            await rag.initialize()
            result = await rag.retrieve(query)
            for c in (result.retrieved_chunks or [])[:3]:
                bits.append(f"[rag/{c.get('source', '?')}] {c.get('text', '')[:300]}")
                sources.append(f"rag:{c.get('source', '?')}")
        except Exception as e:
            logger.debug("rag research: %s", e)

        # Mastery open questions related
        try:
            from haki.mastery import mastery
            for t in mastery.weakest(3):
                if t.open_questions:
                    bits.append(f"[mastery-gap/{t.id}] open: {t.open_questions[0]}")
        except Exception:
            pass

        return bits, sources

    async def _experiment(self, query: str, topics: list) -> tuple[bool, str]:
        """
        Experiment path:
        - Self/lab questions → one evolve_once (may promote brain)
        - Other unknowns → structured hypothesis + store trial result in memory
        """
        from haki.mastery import mastery
        from haki.memory import memory, MemoryNode

        q = query.lower()
        topic_id = topics[0].id if topics else "self"
        note = ""

        # Self-improvement experiments go through Lab
        if any(k in q for k in ("evolve", "improve yourself", "master", "lab", "fine-tune", "specialized model")):
            try:
                from haki.lab import lab
                await lab.initialize()
                result = await lab.evolve_once(epochs=1)
                ok = result.status == "success"
                note = (
                    f"Lab experiment {result.id}: status={result.status} "
                    f"val_bpb={result.val_bpb} {result.description_text}"
                )
                mastery.record_experiment("lab-evolve", ok, note)
                mastery.record_experiment("self", ok, note)
                return ok, note
            except Exception as e:
                note = f"Lab experiment failed: {e}"
                mastery.record_experiment("lab-evolve", False, note)
                return False, note

        # Generic experiment: form hypothesis, store as insight, slight mastery bump for process
        hypothesis = (
            f"Hypothesis for '{query[:120]}': "
            f"I lack sufficient evidence. Next: gather sources, then re-test confidence."
        )
        try:
            node = MemoryNode(
                id=f"exp-{uuid.uuid4().hex[:10]}",
                content=hypothesis,
                role="insight",
                importance=0.6,
                metadata={"type": "experiment", "query": query[:200]},
            )
            await memory.store_memory(node)
            mastery.record_experiment(topic_id, True, "stored hypothesis experiment")
            note = hypothesis
            return True, note
        except Exception as e:
            mastery.record_experiment(topic_id, False, str(e))
            return False, f"Experiment store failed: {e}"

    async def _synthesize(
        self,
        query: str,
        research_bits: list[str],
        conf: float,
        trace: ThoughtTrace,
    ) -> tuple[str, str, int]:
        from haki.brain import brain

        card = brain.model_card()
        gen = int(card.get("generation") or 0)

        # Structural answer first (always correct about process)
        structural = self._structural_answer(query, research_bits, conf, trace)

        # Optional neural polish / expansion if local model loaded
        if brain.local_loaded:
            try:
                prompt = self._neural_prompt(query, research_bits, structural)
                # Use internal generate path via think — but avoid recursion into specialized brain
                # Call neural generate only
                if brain._model is not None:
                    nr = await brain._generate(prompt)
                    if nr.text and not nr.error and len(nr.text) > 20:
                        # Prefer neural if it looks coherent; keep structural as backup prefix if thin
                        text = nr.text.strip()
                        if conf < 0.3 and research_bits:
                            text = structural + "\n\n---\n(local model)\n" + text
                        return text, nr.model or card.get("base_model") or "local", gen
            except Exception as e:
                logger.debug("neural synthesize: %s", e)

        return structural, "specialized-brain", gen

    def _structural_answer(
        self,
        query: str,
        research_bits: list[str],
        conf: float,
        trace: ThoughtTrace,
    ) -> str:
        q = query.lower().strip()
        lines: list[str] = []

        # Identity / self
        if any(k in q for k in ("who are you", "what are you", "what is haki")):
            lines.append(
                "I am **Haki's specialized brain** — a local cognitive runtime. "
                "I do not use a cloud LLM API. I run a tiny local model when weights are loaded, "
                "and I improve myself via Lab (LoRA → promote → generation N+1)."
            )
            lines.append(
                "When I do not know something, I **research** (memory, wiki, RAG) and if still weak I **experiment** "
                "(hypothesis + Lab evolve for self-improvement)."
            )
            return "\n".join(lines)

        if any(k in q for k in ("how do you think", "how do you learn", "master yourself")):
            lines.append("**Thinking loop:** assess → research → experiment → synthesize → learn.")
            lines.append(f"This episode phases: {', '.join(trace.phases)}")
            lines.append(f"Assessed confidence: {conf:.2f}")
            lines.append(
                "Mastery is stored in `~/.haki/mastery.json`. "
                "Self-replacement adapters live in `~/.haki/lab/active_model.json`."
            )
            return "\n".join(lines)

        # Generic synthesis from research
        if research_bits:
            lines.append(f"**Confidence:** {conf:.2f} · **Topics:** {', '.join(trace.topics) or 'general'}")
            lines.append("**What I found:**")
            for b in research_bits[:6]:
                lines.append(f"- {b[:240]}")
            if conf < KNOW_THRESHOLD:
                lines.append(
                    "\nI still treat this as **partial knowledge**. "
                    "I logged gaps to mastery and will improve with more evidence / experiments."
                )
            else:
                lines.append("\nI can answer from this evidence. Confidence will rise with successful reuse.")
            return "\n".join(lines)

        # True unknown
        return (
            f"I do not yet know enough about: «{query[:180]}».\n\n"
            f"Phases run: {', '.join(trace.phases)}. Confidence={conf:.2f}.\n"
            "I recorded this as a mastery gap. Feed me wiki sources (`haki wiki ingest`) or chat more, "
            "then run `haki evolve` so Lab can specialize me. "
            "I will re-research and re-experiment until confidence rises."
        )

    def _neural_prompt(self, query: str, research_bits: list[str], structural: str) -> str:
        ctx = "\n".join(research_bits[:4])[:1200]
        return (
            f"You are Haki, a local-only cognitive OS. Use the evidence. Be concise.\n"
            f"Evidence:\n{ctx}\n\n"
            f"Draft answer:\n{structural[:800]}\n\n"
            f"User question: {query}\n"
            f"Final answer:"
        )

    async def _learn(
        self,
        query: str,
        answer: str,
        conf: float,
        topics: list,
        trace: ThoughtTrace,
    ) -> None:
        from haki.mastery import mastery
        from haki.memory import memory
        from haki.mastery import _slug

        topic_id = topics[0].id if topics else _slug(query[:40])
        if conf >= KNOW_THRESHOLD:
            mastery.record_evidence(topic_id, delta=0.04, note=f"answered: {query[:80]}")
        else:
            mastery.record_gap(topic_id, query)

        try:
            await memory.learn_from_interaction(query, answer)
        except Exception as e:
            logger.debug("learn_from_interaction: %s", e)

        # Continuous self-mastery pressure: if average confidence low, note it
        stats = mastery.stats()
        if stats.get("avg_confidence", 1) < 0.4:
            mastery.record_gap("self", "Average mastery low — need more research/experiments")

    def recent_traces(self, n: int = 10) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._traces[-n:]]


# Singleton specialized brain
specialized_brain = SpecializedBrain()
