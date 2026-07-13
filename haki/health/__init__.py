"""
Self-Healing module — health monitoring, auto-recovery, rollback.

Continuously monitors all subsystems, detects failures, and attempts recovery.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from haki.config import config
from haki.daemon.bus import bus, Event
from haki.organism import Organism

logger = logging.getLogger(__name__)


class ComponentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    name: str
    status: ComponentStatus
    latency_ms: float = 0.0
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemHealth:
    """Aggregated health report."""
    overall: ComponentStatus = ComponentStatus.UNKNOWN
    checks: list[HealthCheck] = field(default_factory=list)
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0

    def to_dict(self) -> dict:
        return {
            "overall": self.overall.value,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "latency_ms": c.latency_ms,
                    "message": c.message,
                }
                for c in self.checks
            ],
            "uptime_seconds": self.uptime_seconds,
            "memory_usage_mb": self.memory_usage_mb,
        }


class HealthMonitor(Organism):
    """
    Monitors all Haki subsystems and auto-recovers from failures.

    Checks:
    - Brain (narrow + wide model availability)
    - Memory graph (DB connectivity)
    - RAG pipeline (index integrity)
    - Lab (training state)
    - Disk space
    - Message bus
    """

    def __init__(self):
        super().__init__("Health")
        self._checks: dict[str, Callable] = {}
        self._results: dict[str, HealthCheck] = {}
        self._start_time = time.perf_counter()
        self._running = False
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        self._checks["brain"] = self._check_brain
        self._checks["memory"] = self._check_memory
        self._checks["rag"] = self._check_rag
        self._checks["wiki"] = self._check_wiki
        self._checks["disk"] = self._check_disk
        self._checks["bus"] = self._check_bus

    def register_check(self, name: str, callback: Callable) -> None:
        """Register a custom health check callback."""
        self._checks[name] = callback

    async def run(self) -> None:
        """Continuous monitoring loop."""
        self._running = True
        logger.info("Health monitor started (interval=%ds).", config.health_check_interval_seconds)

        while self._running:
            try:
                await self.check_all()
                # Publish health status to bus
                report = self.get_report()
                await bus.publish(Event(
                    topic="haki.health",
                    payload=report.to_dict(),
                    source="health",
                ))
            except Exception:
                logger.exception("Health check loop error")
            await asyncio.sleep(config.health_check_interval_seconds)

    async def check_all(self) -> SystemHealth:
        """Run all registered health checks."""
        report = SystemHealth()
        report.uptime_seconds = time.perf_counter() - self._start_time

        for name, check_fn in self._checks.items():
            start = time.perf_counter()
            try:
                if asyncio.iscoroutinefunction(check_fn):
                    result = await check_fn()
                else:
                    result = check_fn()
                result.latency_ms = (time.perf_counter() - start) * 1000
            except Exception as e:
                result = HealthCheck(
                    name=name,
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Check failed: {e}",
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
            self._results[name] = result
            report.checks.append(result)

        # Aggregate
        statuses = [c.status for c in report.checks]
        if any(s == ComponentStatus.UNHEALTHY for s in statuses):
            report.overall = ComponentStatus.UNHEALTHY
        elif any(s == ComponentStatus.DEGRADED for s in statuses):
            report.overall = ComponentStatus.DEGRADED
        else:
            report.overall = ComponentStatus.HEALTHY

        # Memory usage
        try:
            import psutil
            process = psutil.Process()
            report.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            pass

        return report

    def get_report(self) -> SystemHealth:
        """Get the latest health report."""
        report = SystemHealth()
        report.uptime_seconds = time.perf_counter() - self._start_time
        report.checks = list(self._results.values())
        statuses = [c.status for c in report.checks]
        if any(s == ComponentStatus.UNHEALTHY for s in statuses):
            report.overall = ComponentStatus.UNHEALTHY
        elif any(s == ComponentStatus.DEGRADED for s in statuses):
            report.overall = ComponentStatus.DEGRADED
        elif statuses:
            report.overall = ComponentStatus.HEALTHY
        return report

    # --- Default checks ---

    async def _check_brain(self) -> HealthCheck:
        """Local-only brain: not loading weights is OK (specialized loop works offline)."""
        from haki.brain import brain

        # Soft structural init — never download model during health
        if not brain._initialized:
            brain._initialized = True

        card = brain.model_card()
        base = card.get("base_model") or "?"
        gen = card.get("generation", 0)
        adapter = card.get("adapter_path")

        if brain.local_loaded:
            msg = f"local loaded gen={gen} base={base}"
            if adapter:
                msg += " +adapter"
            return HealthCheck(name="brain", status=ComponentStatus.HEALTHY, message=msg)

        # Weights not in RAM: degraded, not a crash — expected until chat/evolve loads them
        msg = (
            f"local-only idle gen={gen} base={base} "
            f"(weights not in RAM — run `haki brain` or `haki chat` to load)"
        )
        if adapter:
            msg = f"local-only adapter registered gen={gen} (not loaded in RAM)"
        if card.get("load_error"):
            msg = f"fallback: {card['load_error'][:80]}"
        return HealthCheck(name="brain", status=ComponentStatus.DEGRADED, message=msg)

    async def _check_memory(self) -> HealthCheck:
        from haki.memory import memory
        try:
            # Prefer light path: ensure SQLite without re-logging embedding every time
            if not memory._initialized:
                await memory.initialize()
            nodes = await memory.get_all()
            emb = "emb=on" if memory._embedding_model is not None else "emb=off"
            return HealthCheck(
                name="memory",
                status=ComponentStatus.HEALTHY,
                message=f"{len(nodes)} memories ({emb})",
            )
        except Exception as e:
            return HealthCheck(name="memory", status=ComponentStatus.UNHEALTHY, message=str(e))

    async def _check_rag(self) -> HealthCheck:
        from haki.rag import rag
        try:
            ready = getattr(rag, "_doc_index", None) is not None
            status = ComponentStatus.HEALTHY if ready else ComponentStatus.DEGRADED
            msg = "index ready" if ready else "no docs indexed (run haki ingest)"
            return HealthCheck(name="rag", status=status, message=msg)
        except Exception as e:
            return HealthCheck(name="rag", status=ComponentStatus.UNHEALTHY, message=str(e))

    async def _check_wiki(self) -> HealthCheck:
        from haki.wiki import wiki
        try:
            if not getattr(wiki, "_initialized", False):
                # Don't force full init if path missing — count pages if any
                try:
                    await wiki.initialize()
                except Exception:
                    pass
            pages = await wiki.get_all_pages()
            n = len(pages)
            if n == 0:
                return HealthCheck(
                    name="wiki",
                    status=ComponentStatus.DEGRADED,
                    message="0 pages (run haki wiki init + ingest)",
                )
            return HealthCheck(name="wiki", status=ComponentStatus.HEALTHY, message=f"{n} pages")
        except Exception as e:
            return HealthCheck(name="wiki", status=ComponentStatus.UNHEALTHY, message=str(e))

    def _check_disk(self) -> HealthCheck:
        try:
            import shutil
            usage = shutil.disk_usage(config.data_dir)
            free_gb = usage.free / (1024**3)
            if free_gb < 1.0:
                return HealthCheck(name="disk", status=ComponentStatus.UNHEALTHY,
                                 message=f"Low disk: {free_gb:.1f}GB free")
            return HealthCheck(name="disk", status=ComponentStatus.HEALTHY,
                             message=f"{free_gb:.1f}GB free")
        except Exception as e:
            return HealthCheck(name="disk", status=ComponentStatus.DEGRADED,
                             message=str(e))

    def _check_bus(self) -> HealthCheck:
        recent = bus.recent(n=5)
        return HealthCheck(name="bus", status=ComponentStatus.HEALTHY,
                         message=f"{len(recent)} recent events")

    async def attempt_recovery(self, component: str) -> bool:
        """Attempt to recover a failed component."""
        logger.info("Attempting recovery of %s...", component)
        try:
            if component == "memory":
                from haki.memory import memory
                memory._initialized = False
                await memory.initialize()
                self.pulse("recover_memory")
                return True
            elif component == "rag":
                from haki.rag import rag
                await rag.initialize()
                self.pulse("recover_rag")
                return True
            elif component == "wiki":
                from haki.wiki import wiki
                wiki._initialized = False
                await wiki.initialize()
                self.pulse("recover_wiki")
                return True
            elif component == "brain":
                from haki.brain import brain
                # Low-risk: don't trigger large downloads in health recovery
                ok = brain.wide_configured or brain.narrow_loaded
                if not brain._initialized:
                    brain._initialized = True
                self.pulse("recover_brain")
                return ok
            elif component == "lab":
                from haki.lab import lab
                await lab.initialize()
                self.pulse("recover_lab")
                return True
        except Exception as e:
            logger.exception("Recovery failed for %s: %s", component, e)
            self.error()
            return False
        return False

    def stop(self) -> None:
        self._running = False


# Singleton
monitor = HealthMonitor()
