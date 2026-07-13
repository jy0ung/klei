"""Haki daemon — main orchestration loop running the message bus and health monitor."""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

from haki.config import config
from haki.daemon.bus import bus, Event
from haki.health.monitor import HealthMonitor

logger = logging.getLogger(__name__)


class HakiDaemon:
    """Top-level daemon that keeps all subsystems alive."""

    def __init__(self) -> None:
        self.monitor = HealthMonitor()
        self._tasks: list[asyncio.Task] = []
        self._shutdown = asyncio.Event()

    async def start(self) -> None:
        logger.info("Starting Haki daemon...")
        await bus.publish(Event(topic="haki.start", payload={}, source="daemon"))
        bus.subscribe("haki.shutdown", self._on_shutdown)

        # Start health monitor
        self._tasks.append(asyncio.create_task(self.monitor.run()))

        await bus.publish(Event(topic="haki.ready", payload={}, source="daemon"))
        logger.info("Haki daemon ready.")

        # Wait for shutdown
        await self._shutdown.wait()

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
