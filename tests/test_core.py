"""Tests for Haki core modules."""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

# Ensure haki is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def tmp_haki_dir(tmp_path):
    """Create a temporary Haki data directory."""
    import haki.config
    haki.config.config.data_dir = tmp_path
    haki.config.config.memory_db = tmp_path / "memory.db"
    haki.config.config.lab_dir = tmp_path / "lab"
    haki.config.config.models_dir = tmp_path / "models"
    return tmp_path


@pytest.mark.asyncio
async def test_memory_store_and_recall(tmp_haki_dir):
    """Test storing and searching memories."""
    from haki.memory import memory, MemoryNode

    await memory.initialize()

    # Store a memory
    node = MemoryNode(
        id="test-1",
        content="User likes Python programming",
        role="insight",
        importance=1.0,
    )
    await memory.store_memory(node)

    # Retrieve
    all_nodes = await memory.get_all()
    assert len(all_nodes) >= 1
    assert any("Python" in n.content for n in all_nodes)


@pytest.mark.asyncio
async def test_memory_interaction_logging(tmp_haki_dir):
    """Test interaction logging."""
    from haki.memory import memory

    await memory.initialize()
    await memory.store_interaction("Hello", "Hi there!", tier="wide")

    interactions = await memory.get_recent_interactions(n=10)
    assert len(interactions) >= 1
    assert interactions[0]["user_input"] == "Hello"


@pytest.mark.asyncio
async def test_brain_routing():
    """Test brain tier routing logic."""
    from haki.brain import Brain, TierChoice

    b = Brain()
    # Simple query should route to narrow
    assert b._is_simple_query("What time is it?")
    assert b._is_simple_query("Hello")
    # Complex query should route to wide
    assert not b._is_simple_query("Explain quantum computing in detail with mathematical proofs")


@pytest.mark.asyncio
async def test_health_monitor(tmp_haki_dir):
    """Test health monitor runs checks."""
    from haki.health import monitor

    report = await monitor.check_all()
    assert report.overall.value in ("healthy", "degraded", "unhealthy")
    assert len(report.checks) >= 3


@pytest.mark.asyncio
async def test_rag_chunking():
    """Test RAG text chunking."""
    from haki.rag import rag

    text = " ".join(["word"] * 2000)
    chunks = rag._chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


@pytest.mark.asyncio
async def test_bus_pubsub():
    """Test message bus pub/sub."""
    from haki.daemon.bus import bus, Event

    received = []

    async def handler(event):
        received.append(event)

    bus.subscribe("test.topic", handler)
    await bus.publish(Event(topic="test.topic", payload={"msg": "hello"}, source="test"))
    await asyncio.sleep(0.01)  # let async handler run

    assert len(received) == 1
    assert received[0].payload["msg"] == "hello"


def test_config_defaults():
    """Test config loads with defaults."""
    from haki.config import config
    assert config.narrow_model_id
    assert config.data_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
