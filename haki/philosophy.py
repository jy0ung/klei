"""
Becoming — the philosophical core of Haki's living architecture.

"If the universe is constantly expanding, then stasis is an illusion.
Nothing — not matter, not thought, not identity — is ever truly still.
To exist is to be in motion, to be becoming rather than being."

This module implements the self-questioning protocol: the system's ability
to generate its own questions, probe its identity, and initiate transformation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TensionType(str, Enum):
    """A tension is a pull toward transformation — the engine of becoming."""
    CONTRADICTION = "contradiction"      # Two beliefs conflict
    GAP = "gap"                           # Missing knowledge at the boundary
    NOVELTY = "novelty"                   # New data doesn't fit existing models
    STASIS = "stasis"                     # Too much stability, risk of death
    GROWTH = "growth"                     # Momentum toward new synthesis


@dataclass
class Tension:
    """A detected tension — a pressure point that demands transformation."""
    type: TensionType
    description: str
    intensity: float  # 0.0 to 1.0
    sources: list[str] = field(default_factory=list)
    suggested_action: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"[{self.type.value}] {self.description} (intensity={self.intensity:.2f})"


@dataclass
class Question:
    """A question the system generates for itself — the fuel of becoming."""
    text: str
    source_tension: Tension | None
    depth: int  # How meta (0=surface, 3=identity-question)
    created_at: datetime = field(default_factory=datetime.utcnow)
    answered: bool = False
    answer: str = ""


class Becoming:
    """
    The self-questioning protocol — the system's capacity to generate
    its own tensions and questions, driving continuous transformation.
    
    Without this, the system is a static repository. With it, the system
    is an active process of inquiry — it doesn't just store knowledge,
    it hunts for the boundaries of its own understanding.
    """

    # Generic probing templates — the system applies these to itself
    PROBES = [
        # Contradiction probes
        "What two beliefs in my wiki contradict each other most strongly?",
        "Where has recent evidence challenged an older, confident claim?",
        "What entity page has conflicting descriptions from different sources?",
        
        # Gap probes  
        "What concept is repeatedly mentioned but lacks its own page?",
        "What question have I been unable to answer due to missing knowledge?",
        "Where does my index have clusters with no cross-links between them?",
        
        # Novelty probes
        "What new source challenged the most existing assumptions?",
        "What synthesis emerged recently that changed how I see existing knowledge?",
        "What connection between entities have I not yet explored?",
        
        # Stasis probes
        "What pages have been unchanged for weeks but have new sources available?",
        "What routine am I doing that has stopped being useful?",
        "What would I do differently if I were starting from scratch?",
        
        # Identity probes (deepest)
        "What is my blind spot — what kind of question do I consistently fail at?",
        "How has my understanding of my user changed in the last month?",
        "What do I think is true that I have never actually verified?",
    ]

    async def scan_for_tensions(self, context: dict[str, Any]) -> list[Tension]:
        """
        Scan the current state for tensions — pressures toward transformation.
        
        In a full implementation, this queries the wiki, memory, lab results,
        and health to detect contradictions, gaps, novelty, and stasis.
        """
        tensions: list[Tension] = []

        # Check wiki stats
        wiki_stats = context.get("wiki_stats", {})
        orphan_count = wiki_stats.get("orphan_pages", 0)
        stale_count = wiki_stats.get("stale_pages", 0)
        total_pages = wiki_stats.get("total_pages", 0)

        if orphan_count > 5:
            tensions.append(Tension(
                type=TensionType.GAP,
                description=f"{orphan_count} orphan pages — knowledge exists but isn't connected",
                intensity=min(orphan_count / 20.0, 1.0),
                suggested_action="Propose cross-linking the orphaned pages",
            ))

        if stale_count > 3:
            tensions.append(Tension(
                type=TensionType.STASIS,
                description=f"{stale_count} stale pages — knowledge frozen, sources may have updated",
                intensity=min(stale_count / 10.0, 1.0),
                suggested_action="Schedule a refresh pass on stale pages",
            ))

        # Check memory stats
        memory_stats = context.get("memory_stats", {})
        insight_count = memory_stats.get("insights", 0)
        interaction_count = memory_stats.get("interactions", 0)

        if interaction_count > 50 and insight_count < 5:
            tensions.append(Tension(
                type=TensionType.GAP,
                description=f"Many interactions ({interaction_count}) but few insights ({insight_count}) — untapped potential",
                intensity=0.6,
                suggested_action="Run a insights-extraction pass over recent interactions",
            ))

        # Check lab stats
        lab_stats = context.get("lab_stats", {})
        experiment_count = lab_stats.get("experiments", 0)
        best_bpb = lab_stats.get("best_bpb")

        if experiment_count > 5 and best_bpb and best_bpb > 1.0:
            tensions.append(Tension(
                type=TensionType.NOVELTY,
                description=f"{experiment_count} experiments but val_bpb still {best_bpb:.4f} — not converging",
                intensity=0.7,
                suggested_action="Try a different approach: change base model or training data strategy",
            ))

        # Meta: check for overall stasis
        health_stats = context.get("health_stats", {})
        uptime = health_stats.get("uptime_seconds", 0)
        last_change = health_stats.get("last_meaningful_change_seconds_ago", 0)

        if uptime > 3600 and last_change > 7200:
            tensions.append(Tension(
                type=TensionType.STASIS,
                description=f"Uptime {uptime/3600:.1f}h but no meaningful change in {last_change/3600:.1f}h — risk of stasis",
                intensity=0.5,
                suggested_action="Force a structural change: merge, split, or challenge an assumption",
            ))

        return tensions

    async def generate_question(self, tension: Tension | None = None) -> Question:
        """
        Generate a question from a tension, or a random deep probe.
        Becoming is driven by questions — the system asks itself what it doesn't know.
        """
        import random

        if tension:
            # Question from tension
            if tension.type == TensionType.CONTRADICTION:
                return Question(
                    text=f"How do I resolve: {tension.description}",
                    source_tension=tension,
                    depth=1,
                )
            elif tension.type == TensionType.GAP:
                return Question(
                    text=f"What would I need to know to fill the gap: {tension.description}",
                    source_tension=tension,
                    depth=1,
                )
            elif tension.type == TensionType.NOVELTY:
                return Question(
                    text=f"How does {tension.description} change what I thought I knew?",
                    source_tension=tension,
                    depth=2,
                )
            elif tension.type == TensionType.STASIS:
                return Question(
                    text=f"What belief am I holding onto that is preventing growth?",
                    source_tension=tension,
                    depth=2,
                )
            else:
                return Question(
                    text=tension.description,
                    source_tension=tension,
                    depth=1,
                )
        else:
            # Deep questioning — no specific tension, just probing
            depth = random.randint(0, 3)
            probe = random.choice(self.PROBES)
            return Question(
                text=probe,
                source_tension=None,
                depth=depth,
            )

    async def propose_transformation(self, tensions: list[Tension]) -> dict[str, Any]:
        """
        Propose a structural transformation based on accumulated tensions.
        This is identity-level change — the system changes how it operates.
        """
        if not tensions:
            return {"action": "none", "reason": "no tensions"}

        # Pick the strongest tension
        strongest = max(tensions, key=lambda t: t.intensity)

        if strongest.type == TensionType.STASIS and strongest.intensity > 0.7:
            return {
                "action": "force_restructure",
                "reason": "stasis critical",
                "details": "Force merge or split of knowledge clusters",
            }
        elif strongest.type == TensionType.GAP:
            return {
                "action": "expand_boundary",
                "reason": strongest.description,
                "details": "Seek new sources or perspectives",
            }
        elif strongest.type == TensionType.NOVELTY:
            return {
                "action": "integrate_novelty",
                "reason": strongest.description,
                "details": "Update models and re-integrate",
            }
        else:
            return {
                "action": "incremental_change",
                "reason": strongest.description,
                "details": strongest.suggested_action,
            }


# Global becoming process — imported everywhere
becoming = Becoming()
