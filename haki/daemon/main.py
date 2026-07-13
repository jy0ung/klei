"""
Haki daemon — main orchestration loop running the message bus, health monitor,
and the becoming process (the self-questioning protocol that drives transformation).
"""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

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
        self._tensions: list[Tension] = []

    async def start(self) -> None:
        logger.info("Starting Haki daemon...")
        await bus.publish(Event(topic="haki.start", payload={}, source="daemon"))
        bus.subscribe("haki.shutdown", self._on_shutdown)

        # Start health monitor
        self._tasks.append(asyncio.create_task(self.monitor.run()))

        # Start the becoming process
        self._tasks.append(asyncio.create_task(self._becoming_loop()))

        await bus.publish(Event(topic="haki.ready", payload={}, source="daemon"))
        logger.info("Haki daemon ready.")

        # Wait for shutdown
        await self._shutdown.wait()

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
            "last_meaningful_change_seconds_ago": 0,  # TODO: track
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
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))
    await daemon.start()


from datetime import datetime
