"""
Organism — the living base class for all Haki modules.

Every module in Haki is an organism: it has a lifecycle, metabolism,
and the capacity to adapt. Nothing is static — every component is
a process of becoming rather than a fixed being.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class LifeStage(str, Enum):
    """The lifecycle stages of an organism — birth, growth, maturity, transformation, death."""
    BIRTH = "birth"               # Just initialized
    GROWTH = "growth"             # Accumulating, learning
    MATURITY = "maturity"         # Stable contribution
    TRANSFORMATION = "transformation"  # Undergoing structural change
    DORMANCY = "dormancy"         # Inactive but alive
    DEATH = "death"               # To be replaced


@dataclass
class Metabolism:
    """Tracks the metabolic health of an organism — its energy flow."""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    operations_count: int = 0
    last_operation: str = ""
    total_input_bytes: int = 0
    total_output_bytes: int = 0
    error_count: int = 0

    def pulse(self, operation: str = "", input_bytes: int = 0, output_bytes: int = 0) -> None:
        """Record activity — the organism is alive and doing something."""
        self.last_active = datetime.utcnow()
        self.operations_count += 1
        self.last_operation = operation
        self.total_input_bytes += input_bytes
        self.total_output_bytes += output_bytes

    def error(self) -> None:
        """Record an error — metabolic stress."""
        self.error_count += 1
        self.last_active = datetime.utcnow()

    @property
    def age_seconds(self) -> float:
        return (datetime.utcnow() - self.created_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        return (datetime.utcnow() - self.last_active).total_seconds()

    @property
    def error_rate(self) -> float:
        if self.operations_count == 0:
            return 0.0
        return self.error_count / self.operations_count


class Organism:
    """
    Base class for all living modules.
    
    An organism:
    - Has a lifecycle (birth → growth → maturity → transformation → death)
    - Has metabolism (activity tracking)
    - Can be questioned (what are you? what do you need? what's blocking you?)
    - Can transform (adapt its structure based on experience)
    """

    def __init__(self, name: str):
        self.name = name
        self.stage = LifeStage.BIRTH
        self.metabolism = Metabolism()
        self._adaptations: list[dict[str, Any]] = []
        self._questions_asked: list[str] = []
        self._transformations: list[dict[str, Any]] = []

    def pulse(self, operation: str = "", input_bytes: int = 0, output_bytes: int = 0) -> None:
        """Heartbeat — record that this organism is alive and active."""
        self.metabolism.pulse(operation, input_bytes, output_bytes)
        if self.stage == LifeStage.BIRTH and self.metabolism.operations_count > 3:
            self.stage = LifeStage.GROWTH
        elif self.stage == LifeStage.GROWTH and self.metabolism.operations_count > 20:
            self.stage = LifeStage.MATURITY

    def error(self) -> None:
        """Something went wrong — metabolic stress."""
        self.metabolism.error()

    def ask(self, question: str) -> None:
        """An external agent asks this organism a question."""
        self._questions_asked.append(f"[{datetime.utcnow().isoformat()}] {question}")
        self.pulse("asked")

    def adapt(self, reason: str, change: dict[str, Any]) -> None:
        """
        Record an adaptation — the organism changed itself.
        This is not failure; this is how living things grow.
        """
        self._adaptations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "change": change,
        })
        self.pulse("adapted")
        logger.info("%s adapted: %s", self.name, reason)

    def transform(self, new_structure: dict[str, Any]) -> None:
        """
        Structural transformation — the organism becomes something different.
        This is the deepest kind of change: not just new knowledge, but new ways of knowing.
        """
        old_stage = self.stage
        self.stage = LifeStage.TRANSFORMATION
        self._transformations.append({
            "from_stage": old_stage.value,
            "timestamp": datetime.utcnow().isoformat(),
            "new_structure": new_structure,
        })
        logger.info("%s transforming: %s → transformation", self.name, old_stage.value)

    def get_vitality(self) -> dict[str, Any]:
        """Get a vitality report — how alive is this organism?"""
        return {
            "name": self.name,
            "stage": self.stage.value,
            "age_seconds": self.metabolism.age_seconds,
            "operations": self.metabolism.operations_count,
            "error_rate": self.metabolism.error_rate,
            "adaptations": len(self._adaptations),
            "transformations": len(self._transformations),
            "recent_questions": self._questions_asked[-5:],
        }

    def die(self) -> None:
        """
        This organism reaches end-of-life.
        Death is not failure — it's the necessary end that makes room for new birth.
        In Haki, a dying organism's knowledge is absorbed by others before passing.
        """
        self.stage = LifeStage.DEATH
        logger.info("%s dying after %d operations", self.name, self.metabolism.operations_count)

    @property
    def is_alive(self) -> bool:
        return self.stage != LifeStage.DEATH
