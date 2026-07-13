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
            # Single message mode
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
            # Interactive mode
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

                # Slash commands
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

                # Normal chat
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
    """Quick status overview."""
    console.print(Panel(
        f"[bold]Haki Status[/bold]\n\n"
        f"Narrow model: {config.narrow_model_id}\n"
        f"Wide model: {config.llm_model}\n"
        f"API configured: {bool(config.llm_api_key)}\n"
        f"Data dir: {config.data_dir}\n"
        f"Lab dir: {config.lab_dir}",
        border_style="cyan",
    ))


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


if __name__ == "__main__":
    cli()
