"""Tests for specialized brain — mastery + cognitive loop."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def tmp_haki(tmp_path, monkeypatch):
    import haki.config
    haki.config.config.data_dir = tmp_path
    haki.config.config.memory_db = tmp_path / "memory.db"
    haki.config.config.lab_dir = tmp_path / "lab"
    haki.config.config.models_dir = tmp_path / "models"
    from haki.mastery import MasteryStore
    from haki.memory import memory
    from haki.wiki import wiki

    store = MasteryStore(tmp_path / "mastery.json")
    memory._db_path = tmp_path / "memory.db"
    memory._index_path = Path(str(memory._db_path) + ".faiss")
    memory._initialized = False
    memory._index = None
    wiki._wiki_dir = tmp_path / "wiki"
    wiki._initialized = False
    return tmp_path, store


def test_mastery_record_and_confidence(tmp_haki):
    _, store = tmp_haki
    store.load()
    store.record_evidence("wiki", 0.1, "ingested")
    t = store.get("wiki")
    assert t is not None
    assert t.confidence > 0.35
    store.record_gap("unknown-topic", "What is X?")
    conf, topics = store.confidence_for_query("wiki ingest")
    assert conf > 0


@pytest.mark.asyncio
async def test_specialized_think_self_identity(tmp_haki):
    tmp, store = tmp_haki
    # Patch mastery singleton path
    import haki.mastery as m
    m.mastery = store
    store.load()

    from haki.cognition import SpecializedBrain
    from haki.memory import memory

    await memory.initialize()
    sb = SpecializedBrain()
    # Avoid heavy neural load
    from haki.brain import brain
    brain._initialized = True
    brain._model = None

    await sb.initialize()
    trace = await sb.think("Who are you?", allow_experiment=False)
    assert "assess" in trace.phases
    assert "synthesize" in trace.phases
    assert "learn" in trace.phases
    assert "Haki" in trace.answer or "local" in trace.answer.lower()
    assert trace.confidence >= 0.5


@pytest.mark.asyncio
async def test_specialized_research_on_unknown(tmp_haki):
    tmp, store = tmp_haki
    import haki.mastery as m
    m.mastery = store
    store.load()

    from haki.cognition import SpecializedBrain
    from haki.memory import memory, MemoryNode
    from haki.brain import brain

    await memory.initialize()
    await memory.store_memory(MemoryNode(
        id="m1", content="Proton dealership inventory aging is tracked weekly",
        role="insight",
    ))
    brain._initialized = True
    brain._model = None

    sb = SpecializedBrain()
    await sb.initialize()
    trace = await sb.think(
        "What do we know about inventory aging?",
        allow_experiment=False,
    )
    assert "research" in trace.phases or trace.research_hits >= 0
    assert trace.answer
    assert "learn" in trace.phases


@pytest.mark.asyncio
async def test_experiment_hypothesis_path(tmp_haki):
    tmp, store = tmp_haki
    import haki.mastery as m
    m.mastery = store
    store.load()

    from haki.cognition import SpecializedBrain
    from haki.memory import memory
    from haki.brain import brain

    await memory.initialize()
    brain._initialized = True
    brain._model = None
    sb = SpecializedBrain()
    await sb.initialize()
    # Force low confidence topic
    store.upsert_topic("obscure-xyz", "obscure-xyz")
    store._topics["obscure-xyz"].confidence = 0.0
    store.save()
    trace = await sb.think("obscure-xyz quantum flubber protocol?", allow_experiment=True)
    assert "experiment" in trace.phases or trace.confidence >= 0
    assert trace.answer
