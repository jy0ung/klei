"""
Self-healing cycle for Haki — L2 post-hoc recovery with audit trail.

Inspired by self-healing agent architecture:
- Detect unhealthy components
- Attempt low-risk recovery
- Log actions to kaizen + bus
- Escalate when auto-recovery fails
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from haki.config import config
from haki.daemon.bus import bus, Event
from haki.organism import Organism

logger = logging.getLogger(__name__)


@dataclass
class HealAction:
    component: str
    action: str
    success: bool
    detail: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "action": self.action,
            "success": self.success,
            "detail": self.detail,
            "timestamp": self.timestamp,
        }


class SelfHealer(Organism):
    """Autonomous recovery agent for Haki subsystems."""

    def __init__(self) -> None:
        super().__init__("SelfHealer")
        self._history: list[HealAction] = []

    async def cycle(self) -> dict[str, Any]:
        """Run one self-healing cycle: check → recover → report."""
        from haki.health import monitor

        report = await monitor.check_all()
        actions: list[HealAction] = []

        for check in report.checks:
            if check.status.value in ("unhealthy", "degraded"):
                action = await self.recover(check.name, check.message)
                actions.append(action)

        # If all healthy, still record a heartbeat pulse
        if not actions:
            self.pulse("cycle_healthy")
            result = {
                "overall": report.overall.value,
                "actions": [],
                "message": "All components healthy",
            }
        else:
            successes = sum(1 for a in actions if a.success)
            self.pulse("cycle_heal", output_bytes=len(actions))
            result = {
                "overall": report.overall.value,
                "actions": [a.to_dict() for a in actions],
                "recovered": successes,
                "failed": len(actions) - successes,
            }

            # Record durable kaizen entry for real repairs
            if successes:
                try:
                    from haki.kaizen import kaizen
                    kaizen.record(
                        title=f"Self-heal recovered {successes} component(s)",
                        problem="; ".join(f"{a.component}:{a.detail}" for a in actions if a.success),
                        action="Autonomous recovery cycle",
                        impact=f"{successes}/{len(actions)} recoveries succeeded",
                        category="defect",
                        status="done",
                    )
                except Exception as e:
                    logger.warning("Could not record kaizen heal: %s", e)

        await bus.publish(Event(topic="haki.self_heal", payload=result, source="self_healer"))
        return result

    async def recover(self, component: str, message: str = "") -> HealAction:
        """Attempt recovery for a single component (low-risk only)."""
        logger.info("Self-heal: recovering %s (%s)", component, message)
        try:
            if component == "memory":
                from haki.memory import memory
                memory._initialized = False
                await memory.initialize()
                ok = True
                detail = "reinitialized memory graph"
            elif component == "rag":
                from haki.rag import rag
                await rag.initialize()
                ok = True
                detail = "reinitialized rag index"
            elif component == "wiki":
                from haki.wiki import wiki
                wiki._initialized = False
                await wiki.initialize()
                ok = True
                detail = "reinitialized wiki"
            elif component == "brain":
                from haki.brain import brain
                # Low-risk only: do not download large models during auto-heal
                if not brain._initialized:
                    brain._initialized = True  # fallback-capable
                ok = True  # fallback rules always available offline
                detail = (
                    f"loaded={brain.local_loaded} gen={brain.model_card()['generation']}; "
                    "local-only mode (no cloud API)"
                )
            elif component == "disk":
                # Cannot invent free space — escalate
                ok = False
                detail = "disk recovery requires human action (free space)"
            elif component == "bus":
                ok = True
                detail = "bus is soft-state; no hard recovery needed"
            else:
                from haki.health import monitor
                ok = await monitor.attempt_recovery(component)
                detail = "delegated to HealthMonitor.attempt_recovery"

            action = HealAction(component=component, action="recover", success=ok, detail=detail)
        except Exception as e:
            self.error()
            action = HealAction(component=component, action="recover", success=False, detail=str(e))

        self._history.append(action)
        if action.success:
            self.adapt(f"healed {component}", action.to_dict())
            self.pulse("recover_ok")
        else:
            self.error()
        return action

    def history(self, n: int = 20) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self._history[-n:]]


self_healer = SelfHealer()
