"""
Kaizen — continuous improvement log for Haki.

Implements small, measurable, permanent improvements:
1. Detect waste / defects
2. Make the smallest fix that works
3. Record it so improvements compound
4. Standardize the good change

This is how Haki itself improves without waiting for big redesigns.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from haki.config import config

logger = logging.getLogger(__name__)


@dataclass
class Improvement:
    """A single continuous improvement entry."""
    id: str
    title: str
    problem: str
    action: str
    impact: str
    category: str = "general"  # defect, waste, standardization, measurement, flow
    status: str = "done"  # proposed, done, verified
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KaizenLog:
    """Persistent continuous-improvement log."""

    def __init__(self) -> None:
        self._path = config.data_dir / "kaizen.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        title: str,
        problem: str,
        action: str,
        impact: str,
        category: str = "general",
        status: str = "done",
    ) -> Improvement:
        entry = Improvement(
            id=datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            title=title,
            problem=problem,
            action=action,
            impact=impact,
            category=category,
            status=status,
        )
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")
        logger.info("Kaizen recorded: %s", title)
        return entry

    def list(self, limit: int = 50) -> list[Improvement]:
        if not self._path.exists():
            return []
        rows: list[Improvement] = []
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                rows.append(Improvement(**data))
        return rows[-limit:]

    def stats(self) -> dict[str, Any]:
        items = self.list(limit=10_000)
        by_cat: dict[str, int] = {}
        for item in items:
            by_cat[item.category] = by_cat.get(item.category, 0) + 1
        return {
            "total": len(items),
            "by_category": by_cat,
            "path": str(self._path),
        }


# Seeded improvements from this Kaizen pass (idempotent if re-recorded later)
SEED_IMPROVEMENTS = [
    {
        "title": "Fix CLI lab/rag name shadowing",
        "problem": "CLI commands named lab/rag overwrote module imports, breaking haki lab and haki rag",
        "action": "Import modules as lab_mod/rag_mod and call those explicitly",
        "impact": "Root-cause defect removed; lab/rag commands work again",
        "category": "defect",
    },
    {
        "title": "Fail-fast Lab empty data guard",
        "problem": "fine_tune_model imported torch/transformers before checking training data",
        "action": "Generate/check training data first; return failed result before heavy imports",
        "impact": "Eliminated wasted startup time and confusing OOM/import errors",
        "category": "waste",
    },
    {
        "title": "Wiki content-aware query scoring",
        "problem": "Wiki query only matched title/tags, missing content hits",
        "action": "Score title×3 + tags×2 + content×1 with tokenized matching",
        "impact": "Better retrieval for questions that mention body content",
        "category": "flow",
    },
    {
        "title": "Make Lab and Brain living organisms",
        "problem": "Only Wiki/Daemon pulsed vitality; most modules looked dead",
        "action": "Lab(Organism) + Brain(Organism) with pulse/error on ops",
        "impact": "Status dashboard reflects real activity across core modules",
        "category": "standardization",
    },
]


kaizen = KaizenLog()


def seed_if_empty() -> int:
    """Record seed improvements once if log is empty."""
    if kaizen.list(limit=1):
        return 0
    for item in SEED_IMPROVEMENTS:
        kaizen.record(**item)
    return len(SEED_IMPROVEMENTS)
