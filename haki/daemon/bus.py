"""Message bus for Haki's daemon — minimal pub/sub event system."""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class Event:
    topic: str
    payload: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""


class MessageBus:
    """Async pub/sub event bus that connects all Haki modules."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._log: list[Event] = []
        self._running = False

    def subscribe(self, topic: str, callback: Callable) -> None:
        self._subscribers[topic].append(callback)
        logger.debug("Subscribed to %s → %s", topic, callback.__name__)

    def unsubscribe(self, topic: str, callback: Callable) -> None:
        self._subscribers[topic] = [c for c in self._subscribers[topic] if c != callback]

    async def publish(self, event: Event) -> None:
        self._log.append(event)
        logger.debug("Publishing %s (%s)", event.topic, event.source)
        for cb in self._subscribers.get(event.topic, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(event)
                else:
                    cb(event)
            except Exception:
                logger.exception("Subscriber error on %s", event.topic)

    def publish_sync(self, event: Event) -> None:
        """Fire-and-forget sync publish (creates task on running loop if possible)."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event))
        except RuntimeError:
            # No running loop — best-effort
            self._log.append(event)

    def recent(self, topic: str | None = None, n: int = 50) -> list[Event]:
        events = self._log
        if topic:
            events = [e for e in events if e.topic == topic]
        return events[-n:]


# Global singleton — imported everywhere
bus = MessageBus()
