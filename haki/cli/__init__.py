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
from haki.brain import brain, TierChoice
from haki.memory import memory, MemoryNode
from haki.rag import rag
from haki.health import monitor
from haki.lab import lab
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
@click.option("--message", "-m", help="Single message to send (interactive mode if omitted)")
@click.option("--tier", type=click.Choice(["narrow", "wide"]), default=None, help="Force model tier")
def chat(message: str | None, tier: str | None):
    """Chat with Haki's brain."""

    async def _chat():
        await brain.initialize()
        await memory.initialize()
        await rag.initialize()

        if message:
            tier_choice = None
            if tier == "narrow":
                tier_choice = TierChoice.NARROW
            elif tier == "wide":
                tier_choice = TierChoice.WIDE

            with console.status("[bold cyan]Thinking...[/bold cyan]"):
                result = await brain.think(message, force_tier=tier_choice)
                await memory.learn_from_interaction(message, result.text)

            console.print(Panel(
                Markdown(result.text),
                title=f"🧠 Haki ({result.tier.value}, {result.latency_ms:.0f}ms)",
                border_style="cyan",
            ))
        else:
            console.print(Panel(
                "[bold]Haki Chat[/bold] — type 'quit' or 'exit' to stop.\n"
                "Commands: /health, /memory, /search <query>, /remember <text>",
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
                elif user_input == "/memory":
                    nodes = await memory.get_all()
                    for n in nodes[-10:]:
                        console.print(f"[dim][{n.role}][/dim] {n.content[:100]}")
                    continue
                elif user_input.startswith("/search "):
                    query = user_input[8:]
                    results = await memory.search(query)
                    for r in results:
                        console.print(f"[yellow]→[/yellow] {r.content[:100]}")
                    continue
                elif user_input.startswith("/remember "):
                    text = user_input[10:]
                    from haki.memory import MemoryNode
                    import uuid
                    from datetime import datetime
                    node = MemoryNode(id=str(uuid.uuid4()), content=text, role="insight")
                    await memory.store_memory(node)
                    console.print("[green]Stored.[/green]")
                    continue

                with console.status("[bold cyan]Thinking...[/bold cyan]"):
                    result = await brain.think(user_input)
                    await memory.learn_from_interaction(user_input, result.text)

                console.print(Panel(
                    Markdown(result.text),
                    title=f"Haki ({result.tier.value})",
                    border_style="cyan",
                ))

    asyncio.run(_chat())


@cli.command()
def health():
    """Check Haki's system health."""

    async def _check():
        await memory.initialize()
        await rag.initialize()
        report = await monitor.check_all()
        _print_health(report)

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
        await lab.initialize()

        console.print(Panel(
            "[bold]Haki Lab — Autonomous Model Creation[/bold]\n\n"
            "Generating training data from memory and running fine-tuning...",
            border_style="magenta",
        ))

        with console.status("[bold magenta]Fine-tuning model...[/bold magenta]"):
            result = await lab.fine_tune_model(model_id=model, epochs=epochs)

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
        await rag.initialize()
        await memory.initialize()
        result = await rag.retrieve(query)
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
        from haki.lab import lab
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

        vit = lab.get_vitality() if hasattr(lab, 'get_vitality') else {"stage": "birth", "operations": 0, "error_rate": 0}
        table.add_row("Lab", vit["stage"], str(vit["operations"]), str(int(vit["error_rate"] * vit["operations"])))

        console.print(table)
        console.print(f"\n[bold]Config:[/bold] narrow={config.narrow_model_id}, wide={config.llm_model}")
        console.print(f"[bold]Data:[/bold] {config.data_dir}")

    asyncio.run(_status())


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
        await rag.initialize()
        p = pathlib.Path(path)
        if not p.exists():
            console.print(f"[red]File not found: {path}[/red]")
            return
        text = p.read_text()
        with console.status(f"Ingesting {path}..."):
            await rag.add_document(text, source=p.name)
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


if __name__ == "__main__":
    cli()
