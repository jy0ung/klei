"""
CLI — Command-line interface for Haki.

Rich-based TUI for interacting with the cognitive OS.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from haki.config import config
from haki.brain import brain
from haki.memory import memory, MemoryNode
from haki.rag import rag as rag_mod
from haki.health import monitor
from haki.lab import lab as lab_mod
from haki.daemon.bus import bus

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


@click.group()
def cli():
    """Haki — Cognitive OS with brain, memory, self-healing, and model creation."""
    pass


@cli.command()
def init():
    """Initialize Haki: create directories, download models, prepare environment."""
    from haki.config import config
    import pathlib

    pathlib.Path(config.data_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(config.models_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(config.lab_dir).mkdir(parents=True, exist_ok=True)

    console.print(Panel(
        f"[bold green]Haki initialized![/bold green]\n\n"
        f"Data dir: {config.data_dir}\n"
        f"Models dir: {config.models_dir}\n"
        f"Memory DB: {config.memory_db}\n"
        f"Lab dir: {config.lab_dir}\n\n"
        f"Next: [cyan]haki daemon start[/cyan]",
        title="🧠 Haki",
        border_style="green",
    ))


@cli.command()
def daemon():
    """Start the Haki daemon."""
    from haki.daemon.main import run_daemon
    console.print("[bold green]Starting Haki daemon...[/bold green]")
    asyncio.run(run_daemon())


@cli.command()
@click.option("--message", "-m", help="Single message (interactive if omitted)")
@click.option("--no-experiment", is_flag=True, help="Skip experiment phase (research only)")
def chat(message: str | None, no_experiment: bool):
    """Chat with Haki's specialized brain (assess → research → experiment → learn)."""

    async def _chat():
        from haki.cognition import specialized_brain

        await specialized_brain.initialize()
        await memory.initialize()
        await rag_mod.initialize()

        async def one_turn(user_input: str):
            with console.status("[bold cyan]Thinking (specialized loop)...[/bold cyan]"):
                trace = await specialized_brain.think(
                    user_input, allow_experiment=not no_experiment
                )
            meta = (
                f"phases={'+'.join(trace.phases)} conf={trace.confidence:.2f} "
                f"research={trace.research_hits} exp={trace.experimented} "
                f"gen={trace.generation} ({trace.latency_ms:.0f}ms)"
            )
            console.print(Panel(
                Markdown(trace.answer),
                title=f"🧠 Haki · {meta}",
                border_style="cyan",
            ))

        if message:
            await one_turn(message)
        else:
            console.print(Panel(
                "[bold]Haki Specialized Brain[/bold] — local-only.\n"
                "Loop: assess → research → experiment → synthesize → learn\n"
                "Commands: /health /brain /mastery /evolve /memory /search /remember  |  quit",
                border_style="cyan",
            ))
            while True:
                try:
                    user_input = console.input("[bold blue]You:[/bold blue] ")
                except (KeyboardInterrupt, EOFError):
                    break
                if user_input.lower() in ("quit", "exit", "q"):
                    break
                if not user_input.strip():
                    continue
                if user_input == "/health":
                    report = await monitor.check_all()
                    _print_health(report)
                    continue
                if user_input == "/brain":
                    console.print(brain.model_card())
                    continue
                if user_input == "/mastery":
                    from haki.mastery import mastery
                    mastery.load()
                    for t in mastery.all_topics()[:15]:
                        console.print(
                            f"  [{t.confidence:.2f}] {t.id}: {t.name} "
                            f"(exp={t.experiments} open={len(t.open_questions)})"
                        )
                    console.print(mastery.stats())
                    continue
                if user_input == "/evolve":
                    with console.status("[magenta]Evolving...[/magenta]"):
                        r = await lab_mod.evolve_once()
                    console.print(f"Evolve: {r.status} {r.description_text} val_bpb={r.val_bpb}")
                    continue
                if user_input == "/memory":
                    nodes = await memory.get_all()
                    for n in nodes[-10:]:
                        console.print(f"[dim][{n.role}][/dim] {n.content[:100]}")
                    continue
                if user_input.startswith("/search "):
                    results = await memory.search(user_input[8:])
                    for r in results:
                        console.print(f"[yellow]→[/yellow] {r.content[:100]}")
                    continue
                if user_input.startswith("/remember "):
                    from haki.memory import MemoryNode
                    import uuid as _uuid
                    node = MemoryNode(id=str(_uuid.uuid4()), content=user_input[10:], role="insight")
                    await memory.store_memory(node)
                    console.print("[green]Stored.[/green]")
                    continue
                await one_turn(user_input)

    asyncio.run(_chat())


@cli.command("think")
@click.argument("query")
@click.option("--no-experiment", is_flag=True)
def think_cmd(query: str, no_experiment: bool):
    """One full metacognitive episode (assess → research → experiment → learn)."""

    async def _think():
        from haki.cognition import specialized_brain
        await specialized_brain.initialize()
        with console.status("[cyan]Cognitive loop...[/cyan]"):
            trace = await specialized_brain.think(query, allow_experiment=not no_experiment)
        console.print(Panel(Markdown(trace.answer), title="🧠 Think", border_style="cyan"))
        table = Table(title="Trace")
        table.add_column("Field")
        table.add_column("Value")
        for k, v in trace.to_dict().items():
            if k == "answer":
                continue
            table.add_row(k, str(v)[:80])
        console.print(table)

    asyncio.run(_think())


@cli.command("mastery")
def mastery_cmd():
    """Show mastery map — what Haki knows and open gaps."""
    from haki.mastery import mastery

    mastery.load()
    stats = mastery.stats()
    table = Table(title="🎯 Mastery Map")
    table.add_column("Topic", style="cyan")
    table.add_column("Conf", justify="right")
    table.add_column("Exp", justify="right")
    table.add_column("Open Q")
    for t in mastery.all_topics():
        oq = t.open_questions[0][:40] if t.open_questions else ""
        table.add_row(t.id, f"{t.confidence:.2f}", str(t.experiments), oq)
    console.print(table)
    console.print(
        f"avg={stats['avg_confidence']:.2f} topics={stats['topics']} "
        f"experiments={stats['experiments']} open={stats['open_questions']}"
    )


@cli.command()
def health():
    """Check Haki's system health."""

    async def _check():
        # Quieter health runs (HF/httpx spam is noise)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
        logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.ERROR)

        report = await monitor.check_all()
        _print_health(report)
        # One-line tip when brain weights idle
        from haki.brain import brain
        if not brain.local_loaded:
            console.print(
                "[dim]Tip: brain weights load on demand — "
                "`haki brain` / `haki chat` / successful `haki evolve` promotion.[/dim]"
            )

    asyncio.run(_check())


def _print_health(report):
    """Pretty-print a health report."""
    table = Table(title="🏥 Haki Health Report")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Latency", justify="right")
    table.add_column("Message")

    for check in report.checks:
        status_color = {
            "healthy": "green",
            "degraded": "yellow",
            "unhealthy": "red",
        }.get(check.status.value, "white")
        table.add_row(
            check.name,
            f"[{status_color}]{check.status.value}[/{status_color}]",
            f"{check.latency_ms:.1f}ms",
            check.message,
        )
    console.print(table)
    console.print(f"Uptime: {report.uptime_seconds:.0f}s | Memory: {report.memory_usage_mb:.1f}MB")


@cli.command()
@click.option("--model", "-m", default=None, help="Base model to fine-tune")
@click.option("--epochs", "-e", default=1, type=int, help="Training epochs")
def lab(model: str | None, epochs: int):
    """Run the Lab — fine-tune a specialized model."""

    async def _lab():
        await brain.initialize()
        await memory.initialize()
        await lab_mod.initialize()

        console.print(Panel(
            "[bold]Haki Lab — Autonomous Model Creation[/bold]\n\n"
            "Generating training data from memory and running fine-tuning...",
            border_style="magenta",
        ))

        with console.status("[bold magenta]Fine-tuning model...[/bold magenta]"):
            result = await lab_mod.fine_tune_model(model_id=model, epochs=epochs)

        if result.status == "success":
            console.print(Panel(
                f"[bold green]Experiment complete![/bold green]\n\n"
                f"val_bpb: {result.val_bpb:.4f}\n"
                f"val_loss: {result.val_loss:.4f}\n"
                f"training_seconds: {result.training_seconds:.1f}\n"
                f"peak_vram_mb: {result.peak_vram_mb:.1f}\n"
                f"description: {result.description_text}",
                title=f"Experiment {result.id}",
                border_style="green",
            ))
        else:
            console.print(f"[red]Experiment failed: {result.description_text}[/red]")

    asyncio.run(_lab())


@cli.command()
@click.argument("query")
def rag(query: str):
    """Query the RAG pipeline."""

    async def _rag():
        await rag_mod.initialize()
        await memory.initialize()
        result = await rag_mod.retrieve(query)
        console.print(Panel(
            f"Retrieved {len(result.retrieved_chunks)} chunks:\n\n" +
            "\n".join(f"- [{c.get('source', '?')}] {c['text'][:100]}" for c in result.retrieved_chunks),
            title="RAG Results",
            border_style="yellow",
        ))

    asyncio.run(_rag())


@cli.command()
def status():
    """Quick status overview of all living modules."""

    async def _status():
        from haki.wiki import wiki
        from haki.memory import memory
        from haki.lab import lab as lab_mod
        from haki.brain import brain
        from haki.daemon.main import HakiDaemon

        table = Table(title="🧠 Haki Living System Status")
        table.add_column("Module", style="cyan")
        table.add_column("Stage", style="bold")
        table.add_column("Ops", justify="right")
        table.add_column("Errors", justify="right")

        daemon = HakiDaemon()
        vit = daemon.get_vitality()
        table.add_row("Daemon", vit["stage"], str(vit["operations"]), "0")

        vit = wiki.get_vitality()
        table.add_row("Wiki", vit["stage"], str(vit["operations"]), str(int(vit["error_rate"] * vit["operations"])))

        vit = brain.get_vitality() if hasattr(brain, 'get_vitality') else {"stage": "maturity", "operations": 0, "error_rate": 0}
        table.add_row("Brain", vit["stage"], str(vit["operations"]), str(int(vit["error_rate"] * vit["operations"])))

        vit = lab_mod.get_vitality() if hasattr(lab_mod, 'get_vitality') else {"stage": "birth", "operations": 0, "error_rate": 0}
        table.add_row("Lab", vit["stage"], str(vit["operations"]), str(int(vit["error_rate"] * vit["operations"])))

        console.print(table)
        card = brain.model_card()
        console.print(
            f"\n[bold]Local brain:[/bold] {card['base_model']} gen={card['generation']} "
            f"loaded={card['loaded']} adapter={card['adapter_path']}"
        )
        console.print(f"[bold]Data:[/bold] {config.data_dir}")

    asyncio.run(_status())


@cli.command("evolve")
@click.option("--epochs", "-e", default=1, type=int)
@click.option("--loops", "-n", default=1, type=int, help="Number of self-evolution cycles")
def evolve(epochs: int, loops: int):
    """Self-evolve: Lab trains on memory and replaces the brain if improved."""

    async def _evolve():
        await memory.initialize()
        await lab_mod.initialize()
        console.print(Panel(
            "[bold]Self-evolution[/bold]\n"
            "Local tiny model trains on interactions → promotes better LoRA into the brain.\n"
            "No cloud API.",
            border_style="magenta",
        ))
        for i in range(loops):
            with console.status(f"[magenta]Evolution cycle {i+1}/{loops}...[/magenta]"):
                result = await lab_mod.evolve_once(epochs=epochs)
            color = "green" if result.status == "success" else "red"
            console.print(
                f"[{color}]cycle {i+1}: {result.status}[/{color}] "
                f"val_bpb={result.val_bpb} · {result.description_text}"
            )
        console.print(brain.model_card())

    asyncio.run(_evolve())


@cli.command("brain")
def brain_cmd():
    """Show local brain model card (generation, adapter, load state)."""

    async def _brain():
        await brain.initialize()
        card = brain.model_card()
        console.print(Panel(
            "\n".join(f"[bold]{k}:[/bold] {v}" for k, v in card.items()),
            title="🧠 Local Brain",
            border_style="cyan",
        ))

    asyncio.run(_brain())


@cli.group()
def become():
    """Becoming operations — the self-questioning protocol."""
    pass


@become.command("status")
def become_status():
    """Show the current state of the becoming process."""

    async def _check():
        from haki.philosophy import becoming
        from haki.daemon.main import HakiDaemon

        daemon = HakiDaemon()
        context = await daemon._gather_context()
        tensions = await becoming.scan_for_tensions(context)

        if not tensions:
            console.print("[green]No tensions detected — system is in equilibrium.[/green]")
            return

        table = Table(title="🔍 Becoming: Detected Tensions")
        table.add_column("Type", style="cyan")
        table.add_column("Description")
        table.add_column("Intensity", justify="right")

        for t in tensions:
            color = "red" if t.intensity > 0.7 else "yellow" if t.intensity > 0.4 else "green"
            table.add_row(t.type.value, t.description[:60], f"[{color}]{t.intensity:.2f}[/{color}]")

        console.print(table)

    asyncio.run(_check())


@become.command("question")
def become_question():
    """Generate a question from current tensions."""

    async def _ask():
        from haki.philosophy import becoming
        from haki.daemon.main import HakiDaemon

        daemon = HakiDaemon()
        context = await daemon._gather_context()
        tensions = await becoming.scan_for_tensions(context)

        if tensions:
            q = await becoming.generate_question(tensions[0])
        else:
            q = await becoming.generate_question(None)

        console.print(Panel(
            f"[bold cyan]Question:[/bold cyan] {q.text}\n\n"
            f"Depth: {q.depth} | From tension: {q.source_tension.type.value if q.source_tension else 'probe'}",
            title="🤔 Becoming Question",
            border_style="cyan",
        ))

    asyncio.run(_ask())


@become.command("propose")
def become_propose():
    """Propose a transformation based on current tensions."""

    async def _propose():
        from haki.philosophy import becoming
        from haki.daemon.main import HakiDaemon

        daemon = HakiDaemon()
        context = await daemon._gather_context()
        tensions = await becoming.scan_for_tensions(context)
        proposal = await becoming.propose_transformation(tensions)

        console.print(Panel(
            f"[bold]Action:[/bold] {proposal['action']}\n"
            f"[bold]Reason:[/bold] {proposal.get('reason', 'none')}\n"
            f"[bold]Details:[/bold] {proposal.get('details', '')}",
            title="🔄 Becoming Proposal",
            border_style="magenta",
        ))

    asyncio.run(_propose())


@cli.command()
@click.argument("path")
def ingest(path: str):
    """Ingest a document into RAG knowledge base."""
    import pathlib

    async def _ingest():
        await rag_mod.initialize()
        p = pathlib.Path(path)
        if not p.exists():
            console.print(f"[red]File not found: {path}[/red]")
            return
        text = p.read_text()
        with console.status(f"Ingesting {path}..."):
            await rag_mod.add_document(text, source=p.name)
        console.print(f"[green]Ingested {path}[/green]")

    asyncio.run(_ingest())


@cli.group()
def wiki():
    """Wiki operations: ingest, query, lint."""
    pass


@wiki.command("init")
def wiki_init():
    """Initialize the wiki directory and schema."""

    async def _init():
        from haki.wiki import wiki
        await wiki.initialize()
        console.print(Panel(
            f"[bold green]Wiki initialized![/bold green]\n\n"
            f"Path: {wiki.wiki_path()}\n"
            f"Schema: schema.md\n"
            f"Index: index.md\n"
            f"Log: log.md",
            title="📝 Wiki",
            border_style="green",
        ))

    asyncio.run(_init())


@wiki.command("ingest")
@click.argument("path")
@click.option("--title", "-t", default=None, help="Source title")
@click.option("--entities", "-e", default=None, help="Comma-separated entity list")
@click.option("--concepts", "-c", default=None, help="Comma-separated concept list")
def wiki_ingest(path: str, title: str | None, entities: str | None, concepts: str | None):
    """Ingest a document into the wiki."""
    import pathlib

    async def _ingest():
        from haki.wiki import wiki
        await wiki.initialize()

        p = pathlib.Path(path)
        if not p.exists():
            console.print(f"[red]File not found: {path}[/red]")
            return

        entity_list = [e.strip() for e in entities.split(",")] if entities else []
        concept_list = [c.strip() for c in concepts.split(",")] if concepts else []

        with console.status(f"Ingesting {path}..."):
            result = await wiki.ingest_source(
                p, title=title, entities=entity_list, concepts=concept_list,
            )

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        console.print(Panel(
            f"[bold green]Ingested: {result['source']}[/bold green]\n\n"
            f"Pages touched: {result['count']}\n"
            + "\n".join(f"  - {p}" for p in result["pages_touched"]),
            title="📝 Wiki Ingest",
            border_style="green",
        ))

    asyncio.run(_ingest())


@wiki.command("query")
@click.argument("question")
@click.option("--top-k", "-k", default=5, type=int, help="Number of pages to retrieve")
def wiki_query(question: str, top_k: int):
    """Query the wiki for an answer."""

    async def _query():
        from haki.wiki import wiki
        await wiki.initialize()
        result = await wiki.query(question, top_k=top_k)

        console.print(Panel(
            f"[bold cyan]Question:[/bold cyan] {question}\n\n"
            f"[bold]Sources:[/bold] {len(result['sources'])}\n"
            + "\n".join(f"  - [{s['title']}]({s['path']})" for s in result["sources"])
            + "\n\n[bold]Context:[/bold]\n" + result["context"][:2000],
            title="📝 Wiki Query",
            border_style="cyan",
        ))

    asyncio.run(_query())


@wiki.command("lint")
def wiki_lint():
    """Lint the wiki: find orphans, staleness, contradictions."""

    async def _lint():
        from haki.wiki import wiki
        await wiki.initialize()
        result = await wiki.lint()

        if result.is_clean:
            console.print("[green]Wiki is clean![/green]")
            return

        lines = []
        if result.orphan_pages:
            lines.append(f"[bold]Orphan pages:[/bold] {len(result.orphan_pages)}")
            lines.extend(f"  - {p}" for p in result.orphan_pages[:10])
        if result.stale_pages:
            lines.append(f"[bold]Stale pages:[/bold] {len(result.stale_pages)}")
            lines.extend(f"  - {p}" for p in result.stale_pages[:10])
        if result.suggested_questions:
            lines.append("[bold]Suggested questions:[/bold]")
            lines.extend(f"  - {q}" for q in result.suggested_questions)

        console.print(Panel(
            "\n".join(lines) if lines else "Wiki is clean!",
            title="📝 Wiki Lint",
            border_style="yellow",
        ))

    asyncio.run(_lint())


@wiki.command("status")
def wiki_status():
    """Show wiki statistics."""

    async def _status():
        from haki.wiki import wiki
        await wiki.initialize()
        pages = await wiki.get_all_pages()

        from collections import Counter
        by_type = Counter(p.page_type.value for p in pages)

        table = Table(title="📝 Wiki Statistics")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right")

        for ptype, count in sorted(by_type.items()):
            table.add_row(ptype, str(count))
        table.add_row("[bold]Total[/bold]", str(len(pages)))

        console.print(table)
        console.print(f"Wiki path: {wiki.wiki_path()}")

    asyncio.run(_status())


@cli.command("heal")
def heal():
    """Run one autonomous self-healing cycle."""

    async def _heal():
        from haki.self_heal import self_healer
        await memory.initialize()
        await rag_mod.initialize()
        result = await self_healer.cycle()
        actions = result.get("actions") or []
        if not actions:
            console.print(Panel(
                f"[green]{result.get('message', 'Healthy')}[/green]\nOverall: {result.get('overall')}",
                title="🩹 Self-Heal",
                border_style="green",
            ))
            return
        lines = [f"Overall: {result.get('overall')}", f"Recovered: {result.get('recovered', 0)}", ""]
        for a in actions:
            mark = "✓" if a.get("success") else "✗"
            lines.append(f"{mark} {a.get('component')}: {a.get('detail')}")
        console.print(Panel("\n".join(lines), title="🩹 Self-Heal", border_style="yellow"))

    asyncio.run(_heal())


@cli.group()
def kaizen():
    """Kaizen — continuous improvement log."""
    pass


@kaizen.command("list")
@click.option("--limit", "-n", default=20, type=int)
def kaizen_list(limit: int):
    """List recent continuous improvements."""
    from haki.kaizen import kaizen as klog, seed_if_empty

    seed_if_empty()
    items = klog.list(limit=limit)
    if not items:
        console.print("[yellow]No improvements recorded yet.[/yellow]")
        return

    table = Table(title="📈 Kaizen Log")
    table.add_column("When", style="dim")
    table.add_column("Category", style="cyan")
    table.add_column("Title")
    table.add_column("Impact")

    for item in items:
        table.add_row(
            item.created_at[:16],
            item.category,
            item.title[:40],
            item.impact[:50],
        )
    console.print(table)


@kaizen.command("add")
@click.option("--title", "-t", required=True)
@click.option("--problem", "-p", required=True)
@click.option("--action", "-a", required=True)
@click.option("--impact", "-i", required=True)
@click.option("--category", "-c", default="general")
def kaizen_add(title: str, problem: str, action: str, impact: str, category: str):
    """Record a continuous improvement."""
    from haki.kaizen import kaizen as klog

    entry = klog.record(title=title, problem=problem, action=action, impact=impact, category=category)
    console.print(Panel(
        f"[green]Recorded[/green] {entry.id}\n\n"
        f"[bold]{entry.title}[/bold]\n"
        f"Problem: {entry.problem}\n"
        f"Action: {entry.action}\n"
        f"Impact: {entry.impact}",
        title="📈 Kaizen",
        border_style="green",
    ))


@kaizen.command("stats")
def kaizen_stats():
    """Show continuous improvement statistics."""
    from haki.kaizen import kaizen as klog, seed_if_empty

    seed_if_empty()
    stats = klog.stats()
    lines = [f"Total improvements: {stats['total']}", f"Log: {stats['path']}", ""]
    for cat, count in sorted(stats["by_category"].items()):
        lines.append(f"  {cat}: {count}")
    console.print(Panel("\n".join(lines), title="📈 Kaizen Stats", border_style="cyan"))


if __name__ == "__main__":
    cli()
