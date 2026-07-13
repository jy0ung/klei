"""
Mastery — what Haki knows, how well, and what it still needs to learn.

A specialized brain cannot master itself without a durable map of competence.
Each topic has confidence [0,1], evidence, experiments tried, and open questions.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from haki.config import config

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:80] or "unknown"


@dataclass
class MasteryTopic:
    """One domain of competence."""
    id: str
    name: str
    confidence: float = 0.0          # 0 = unknown, 1 = mastered
    evidence_count: int = 0
    experiments: int = 0
    successes: int = 0
    failures: int = 0
    open_questions: list[str] = field(default_factory=list)
    last_practiced: str = field(default_factory=_utc_now)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MasteryTopic":
        return cls(
            id=d["id"],
            name=d.get("name", d["id"]),
            confidence=float(d.get("confidence", 0.0)),
            evidence_count=int(d.get("evidence_count", 0)),
            experiments=int(d.get("experiments", 0)),
            successes=int(d.get("successes", 0)),
            failures=int(d.get("failures", 0)),
            open_questions=list(d.get("open_questions") or []),
            last_practiced=d.get("last_practiced") or _utc_now(),
            notes=d.get("notes") or "",
        )


class MasteryStore:
    """Persistent mastery map under ~/.haki/mastery.json."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (config.data_dir / "mastery.json")
        self._topics: dict[str, MasteryTopic] = {}
        self._loaded = False

    def load(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for item in data.get("topics", []):
                    t = MasteryTopic.from_dict(item)
                    self._topics[t.id] = t
            except Exception as e:
                logger.warning("Mastery load failed: %s", e)
        # Seed self-topics so the brain always has a self-mastery surface
        self._ensure_seed_topics()
        self._loaded = True

    def _ensure_seed_topics(self) -> None:
        seeds = [
            ("self", "Self — how Haki works and improves"),
            ("local-brain", "Local model load, generate, promote"),
            ("lab-evolve", "Lab fine-tune and self-replacement"),
            ("memory", "Memory graph and insights"),
            ("wiki", "Wiki ingest/query/lint"),
            ("health", "Health checks and self-heal"),
        ]
        for tid, name in seeds:
            if tid not in self._topics:
                self._topics[tid] = MasteryTopic(id=tid, name=name, confidence=0.35)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "updated_at": _utc_now(),
            "topics": [t.to_dict() for t in self._topics.values()],
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get(self, topic_id: str) -> MasteryTopic | None:
        self.ensure_loaded()
        return self._topics.get(topic_id)

    def all_topics(self) -> list[MasteryTopic]:
        self.ensure_loaded()
        return sorted(self._topics.values(), key=lambda t: t.confidence)

    def upsert_topic(self, name: str, topic_id: str | None = None) -> MasteryTopic:
        self.ensure_loaded()
        tid = topic_id or _slug(name)
        if tid not in self._topics:
            self._topics[tid] = MasteryTopic(id=tid, name=name)
            self.save()
        return self._topics[tid]

    def record_evidence(self, topic_id: str, delta: float = 0.05, note: str = "") -> MasteryTopic:
        """Successful use of knowledge increases confidence (capped)."""
        t = self.upsert_topic(topic_id, topic_id)
        t.evidence_count += 1
        t.confidence = min(1.0, t.confidence + delta)
        t.last_practiced = _utc_now()
        if note:
            t.notes = (t.notes + " | " + note).strip(" |")[-500:]
        self.save()
        return t

    def record_gap(self, topic_id: str, question: str) -> MasteryTopic:
        """Unknown → lower confidence slightly and track open question."""
        t = self.upsert_topic(topic_id, topic_id)
        t.confidence = max(0.0, t.confidence - 0.02)
        if question and question not in t.open_questions:
            t.open_questions.append(question[:200])
            t.open_questions = t.open_questions[-20:]
        t.last_practiced = _utc_now()
        self.save()
        return t

    def record_experiment(self, topic_id: str, success: bool, note: str = "") -> MasteryTopic:
        t = self.upsert_topic(topic_id, topic_id)
        t.experiments += 1
        if success:
            t.successes += 1
            t.confidence = min(1.0, t.confidence + 0.08)
        else:
            t.failures += 1
            t.confidence = max(0.0, t.confidence - 0.03)
        t.last_practiced = _utc_now()
        if note:
            t.notes = (t.notes + " | " + note).strip(" |")[-500:]
        # Close matching open questions on success
        if success and t.open_questions:
            t.open_questions = t.open_questions[1:]
        self.save()
        return t

    def confidence_for_query(self, query: str) -> tuple[float, list[MasteryTopic]]:
        """Heuristic: match query tokens to topic names/ids."""
        self.ensure_loaded()
        q = query.lower()
        words = set(re.findall(r"[a-z0-9]{3,}", q))
        hits: list[tuple[float, MasteryTopic]] = []
        for t in self._topics.values():
            name_words = set(re.findall(r"[a-z0-9]{3,}", (t.name + " " + t.id).lower()))
            overlap = len(words & name_words)
            if overlap or t.id in q or any(w in q for w in t.id.split("-")):
                score = t.confidence + 0.05 * overlap
                hits.append((score, t))
        hits.sort(key=lambda x: x[0], reverse=True)
        if not hits:
            return 0.0, []
        return hits[0][0], [h[1] for h in hits[:5]]

    def weakest(self, n: int = 5) -> list[MasteryTopic]:
        self.ensure_loaded()
        return sorted(self._topics.values(), key=lambda t: t.confidence)[:n]

    def stats(self) -> dict[str, Any]:
        self.ensure_loaded()
        topics = list(self._topics.values())
        if not topics:
            return {"topics": 0, "avg_confidence": 0.0}
        return {
            "topics": len(topics),
            "avg_confidence": sum(t.confidence for t in topics) / len(topics),
            "experiments": sum(t.experiments for t in topics),
            "open_questions": sum(len(t.open_questions) for t in topics),
            "path": str(self._path),
        }


mastery = MasteryStore()
