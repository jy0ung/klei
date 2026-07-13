"""Kaizen-focused regression tests for Haki."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def tmp_haki_dir(tmp_path, monkeypatch):
    import haki.config
    from haki.wiki import wiki
    from haki.lab import lab
    from haki.memory import memory

    haki.config.config.data_dir = tmp_path
    haki.config.config.memory_db = tmp_path / "memory.db"
    haki.config.config.lab_dir = tmp_path / "lab"
    haki.config.config.models_dir = tmp_path / "models"

    # Reset module state for isolation
    wiki._wiki_dir = tmp_path / "wiki"
    wiki._initialized = False
    lab._lab_dir = tmp_path / "lab"
    lab._lab_dir.mkdir(parents=True, exist_ok=True)
    lab._results = []
    memory._db_path = tmp_path / "memory.db"
    memory._index_path = Path(str(memory._db_path) + ".faiss")
    memory._initialized = False
    memory._index = None
    return tmp_path


def test_cli_module_imports_not_shadowed():
    """CLI lab/rag commands must not shadow module objects."""
    from haki.cli import lab_mod, rag_mod
    from haki.lab import Lab
    from haki.rag import RAGPipeline

    assert isinstance(lab_mod, Lab)
    assert isinstance(rag_mod, RAGPipeline)
    assert hasattr(lab_mod, "fine_tune_model")
    assert hasattr(rag_mod, "retrieve")


@pytest.mark.asyncio
async def test_lab_empty_data_fail_fast(tmp_haki_dir):
    """Lab should fail fast with empty data before training."""
    from haki.lab import lab
    from haki.memory import memory

    await memory.initialize()
    await lab.initialize()
    result = await lab.fine_tune_model(epochs=1)
    assert result.status == "failed"
    assert "No training data" in result.description_text


@pytest.mark.asyncio
async def test_wiki_query_matches_content(tmp_haki_dir):
    """Wiki query should find content even when title differs."""
    from haki.wiki import wiki

    await wiki.initialize()
    await wiki.ingest_text(
        title="Vehicle Ops",
        text="Proton dealership inventory aging is tracked weekly for Sabah outlets.",
        entities=["Proton"],
        concepts=["inventory aging"],
    )
    result = await wiki.query("dealership inventory aging")
    assert result["sources"], "Expected content-based wiki hits"
    titles = " ".join(s["title"] for s in result["sources"]).lower()
    assert "vehicle" in titles or "proton" in titles or "inventory" in titles


@pytest.mark.asyncio
async def test_brain_and_lab_are_organisms():
    from haki.brain import brain
    from haki.lab import lab
    from haki.organism import Organism

    assert isinstance(brain, Organism)
    assert isinstance(lab, Organism)
    assert brain.name == "Brain"
    assert lab.name == "Lab"


def test_kaizen_log_records(tmp_haki_dir, monkeypatch):
    from haki.kaizen import KaizenLog

    k = KaizenLog()
    k._path = tmp_haki_dir / "kaizen.jsonl"
    entry = k.record(
        title="test improvement",
        problem="defect",
        action="fix",
        impact="works",
        category="defect",
    )
    items = k.list()
    assert len(items) == 1
    assert items[0].title == "test improvement"
    assert entry.id


def test_brain_routing_heuristic():
    from haki.brain import Brain

    b = Brain()
    assert b._is_simple_query("Hello")
    assert not b._is_simple_query(
        "Explain quantum computing in detail with mathematical proofs and implications"
    )
