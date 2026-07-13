"""
Haki daemon — main orchestration loop running the message bus, health monitor,
and the becoming process (the self-questioning protocol that drives transformation).
"""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime

from haki.config import config
from haki.daemon.bus import bus, Event
from haki.health import HealthMonitor
from haki.philosophy import becoming, Tension
from haki.organism import Organism, LifeStage

logger = logging.getLogger(__name__)


class HakiDaemon(Organism):
    """
    Top-level daemon that keeps all subsystems alive and runs the becoming process.
    
    The daemon is itself a living organism — it has a lifecycle, metabolism,
    and the capacity to transform. It doesn't just maintain; it questions.
    """

    def __init__(self) -> None:
        super().__init__("Daemon")
        self.monitor = HealthMonitor()
        self._tasks: list[asyncio.Task] = []
        self._shutdown = asyncio.Event()
        self._becoming_interval = 300  # Run becoming process every 5 minutes
        self._self_heal_interval = config.self_heal_interval_seconds
        self._tensions: list[Tension] = []
        self._last_meaningful_change = time.perf_counter()

    async def start(self) -> None:
        logger.info("Starting Haki daemon...")
        await bus.publish(Event(topic="haki.start", payload={}, source="daemon"))
        bus.subscribe("haki.shutdown", self._on_shutdown)
        bus.subscribe("haki.self_heal", self._on_self_heal)
        bus.subscribe("haki.becoming", self._on_becoming)
        bus.subscribe("haki.evolve.request", self._on_evolve_request)

        # Start health monitor
        self._tasks.append(asyncio.create_task(self.monitor.run()))

        # Start the becoming process
        self._tasks.append(asyncio.create_task(self._becoming_loop()))

        # Start self-healing cycle
        self._tasks.append(asyncio.create_task(self._self_heal_loop()))

        # Start background evolve worker
        self._tasks.append(asyncio.create_task(self._evolve_worker()))

        await bus.publish(Event(topic="haki.ready", payload={}, source="daemon"))
        logger.info("Haki daemon ready.")

        # Wait for shutdown
        await self._shutdown.wait()

    async def _on_evolve_request(self, event: Event) -> None:
        """CLI `haki evolve` can queue evolve via bus."""
        payload = event.payload or {}
        epochs = int(payload.get("epochs", 1))
        loops = int(payload.get("loops", 1))
        logger.info("Evolve requested: epochs=%d loops=%d", epochs, loops)
        # Set evolve intent so worker picks it up
        self._evolve_epochs = epochs
        self._evolve_loops = loops
        self._evolve_requested = True

    async def _evolve_worker(self) -> None:
        """Background evolve: one cycle at a time, checkpoint after each."""
        self._evolve_requested = False
        self._evolve_epochs = 1
        self._evolve_loops = 0

        from haki.memory import memory
        from haki.lab import lab as lab_mod

        while not self._shutdown.is_set():
            if self._evolve_requested and self._evolve_loops > 0:
                await memory.initialize()
                await lab_mod.initialize()
                for i in range(self._evolve_loops):
                    if self._shutdown.is_set():
                        break
                    logger.info("Background evolve cycle %d/%d", i + 1, self._evolve_loops)
                    self.pulse("evolve_cycle")
                    try:
                        result = await lab_mod.evolve_once(epochs=self._evolve_epochs)
                        self._last_meaningful_change = time.perf_counter()
                        await bus.publish(Event(
                            topic="haki.evolve.result",
                            payload={
                                "cycle": i + 1,
                                "status": result.status,
                                "val_bpb": result.val_bpb,
                                "description": result.description_text,
                            },
                            source="daemon",
                        ))
                        logger.info(
                            "Evolve %d/%d: %s val_bpb=%s %s",
                            i + 1, self._evolve_loops,
                            result.status, result.val_bpb, result.description_text,
                        )
                    except Exception as exc:
                        logger.exception("Background evolve failed: %s", exc)
                        self.error()
                self._evolve_requested = False
                self._evolve_loops = 0
            await asyncio.sleep(1)  # check for requests every second

    async def _self_heal_loop(self) -> None:
        """Periodic autonomous recovery cycle."""
        from haki.self_heal import self_healer
        logger.info("Self-heal process started (interval=%ds).", self._self_heal_interval)
        while not self._shutdown.is_set():
            try:
                await self_healer.cycle()
            except Exception:
                logger.exception("Self-heal cycle error")
            await asyncio.sleep(self._self_heal_interval)

    async def _on_self_heal(self, event: Event) -> None:
        payload = event.payload or {}
        if payload.get("recovered"):
            self._last_meaningful_change = time.perf_counter()
            self.pulse("self_heal_event")

    async def _on_becoming(self, event: Event) -> None:
        self._last_meaningful_change = time.perf_counter()
        self.pulse("becoming_event")

    async def _becoming_loop(self) -> None:
        """
        The becoming process — the system's capacity to question itself
        and initiate transformation. This runs continuously alongside
        the health monitor.
        """
        logger.info("Becoming process started (interval=%ds).", self._becoming_interval)

        while not self._shutdown.is_set():
            try:
                await self._becoming_pass()
            except Exception:
                logger.exception("Becoming pass error")
            await asyncio.sleep(self._becoming_interval)

    async def _becoming_pass(self) -> None:
        """
        A single becoming pass:
        1. Scan for tensions (contradictions, gaps, novelty, stasis)
        2. Generate questions from tensions
        3. Propose transformations
        4. Publish becoming event
        """
        self.pulse("becoming_pass")

        # Gather context from all modules
        context = await self._gather_context()

        # Scan for tensions
        tensions = await becoming.scan_for_tensions(context)
        self._tensions = tensions

        if tensions:
            logger.info("Becoming: %d tensions detected", len(tensions))
            for t in tensions:
                logger.info("  %s", t)

            # Generate questions
            questions = []
            for tension in tensions[:3]:  # Top 3 tensions
                q = await becoming.generate_question(tension)
                questions.append(q)

            # Propose transformation
            proposal = await becoming.propose_transformation(tensions)

            # Publish becoming event
            await bus.publish(Event(
                topic="haki.becoming",
                payload={
                    "tensions": [{"type": t.type.value, "description": t.description, "intensity": t.intensity} for t in tensions],
                    "questions": [q.text for q in questions],
                    "proposal": proposal,
                },
                source="becoming",
            ))

            # Log the becoming pass
            logger.info("Becoming proposal: %s", proposal)
        else:
            logger.debug("Becoming: no tensions detected")

    async def _gather_context(self) -> dict:
        """Gather context from all modules for the becoming process."""
        context = {}

        # Wiki stats
        try:
            from haki.wiki import wiki
            if wiki._initialized:
                pages = await wiki.get_all_pages()
                orphan_count = 0
                stale_count = 0
                for p in pages:
                    # Simple orphan/stale detection
                    if not p.links:
                        orphan_count += 1
                    age = (datetime.utcnow() - p.updated_at).days
                    if age > 30:
                        stale_count += 1
                context["wiki_stats"] = {
                    "total_pages": len(pages),
                    "orphan_pages": orphan_count,
                    "stale_pages": stale_count,
                }
        except Exception:
            pass

        # Memory stats
        try:
            from haki.memory import memory
            interactions = await memory.get_recent_interactions(n=1000)
            all_memories = await memory.get_all()
            context["memory_stats"] = {
                "interactions": len(interactions),
                "insights": len([m for m in all_memories if m.role == "insight"]),
            }
        except Exception:
            pass

        # Lab stats
        try:
            from haki.lab import lab
            results = lab.get_results()
            best_bpb = min((r.val_bpb for r in results if r.val_bpb), default=None)
            context["lab_stats"] = {
                "experiments": len(results),
                "best_bpb": best_bpb,
            }
        except Exception:
            pass

        # Health stats
        report = self.monitor.get_report()
        context["health_stats"] = {
            "uptime_seconds": report.uptime_seconds,
            "last_meaningful_change_seconds_ago": time.perf_counter() - self._last_meaningful_change,
        }

        return context

    async def _on_shutdown(self, event: Event) -> None:
        logger.info("Shutdown signal received.")
        self._shutdown.set()

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        await bus.publish(Event(topic="haki.stop", payload={}, source="daemon"))


async def run_daemon() -> None:
    daemon = HakiDaemon()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))
        except NotImplementedError:
            # Windows often lacks add_signal_handler
            pass
    await daemon.start()
