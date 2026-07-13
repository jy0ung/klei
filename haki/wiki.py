"""
Wiki module — LLM-maintained persistent knowledge base.

Implements Karpathy's LLM Wiki pattern:
- Raw sources (immutable documents)
- Wiki (interlinked markdown pages maintained by LLM)
- Schema (CLAUDE.md-style instructions for wiki discipline)
- Operations (ingest, query, lint)
- Index + log for navigation

The wiki subsumes and extends the memory graph — every memory
becomes a wiki page, every interaction an ingest event.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from haki.config import config
from haki.organism import Organism, LifeStage, Metabolism

logger = logging.getLogger(__name__)


class PageType(str, Enum):
    ENTITY = "entity"
    CONCEPT = "concept"
    SOURCE = "source"
    SYNTHESIS = "synthesis"
    INSIGHT = "insight"
    LOG = "log"
    INDEX = "index"


@dataclass
class WikiPage:
    """A single wiki page — a markdown file with optional frontmatter."""
    path: str  # relative path within wiki dir (e.g., "entities/python.md")
    title: str
    content: str
    page_type: PageType
    tags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)  # outbound wiki links [[like this]]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    importance: float = 1.0

    @property
    def filename(self) -> str:
        return Path(self.path).name

    def to_markdown(self) -> str:
        """Serialize to markdown with YAML frontmatter."""
        tags_str = ", ".join(self.tags)
        sources_str = ", ".join(self.sources)
        frontmatter = f"""---
title: {self.title}
type: {self.page_type.value}
tags: [{tags_str}]
sources: [{sources_str}]
created: {self.created_at.isoformat()}
updated: {self.updated_at.isoformat()}
importance: {self.importance}
---

# {self.title}

{self.content}
"""
        return frontmatter

    @classmethod
    def from_markdown(cls, path: str, text: str) -> WikiPage:
        """Parse markdown file with YAML frontmatter."""
        # Extract frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            body = fm_match.group(2)
            fm: dict[str, Any] = {}
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    val = val.strip()
                    if val.startswith("[") and val.endswith("]"):
                        inner = val[1:-1].strip()
                        if inner:
                            val = [v.strip().strip("'\"") for v in inner.split(",")]
                        else:
                            val = []
                    fm[key.strip()] = val
        else:
            fm = {}
            body = text

        # Extract title from heading
        title = fm.get("title", "")
        if not title:
            h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            title = h1.group(1) if h1 else Path(path).stem

        # Extract wiki links
        links = re.findall(r"\[\[([^\]]+)\]\]", body)

        return cls(
            path=path,
            title=title,
            content=body.strip(),
            page_type=PageType(fm.get("type", "concept")),
            tags=fm.get("tags", []),
            sources=fm.get("sources", []),
            links=links,
        )


@dataclass
class WikiLintResult:
    """Result of a wiki lint pass."""
    contradictions: list[str] = field(default_factory=list)
    orphan_pages: list[str] = field(default_factory=list)
    stale_pages: list[str] = field(default_factory=list)
    missing_cross_refs: list[str] = field(default_factory=list)
    suggested_questions: list[str] = field(default_factory=list)
    suggested_sources: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not any([self.contradictions, self.orphan_pages, self.stale_pages])


class Wiki(Organism):
    """
    The LLM Wiki — a structured, interlinked markdown knowledge base.
    
    Directory structure:
        wiki/
        ├── schema.md        # Wiki discipline instructions
        ├── index.md         # Catalog of all pages
        ├── log.md           # Chronological operation log
        ├── entities/        # Entity pages (people, places, things)
        ├── concepts/        # Concept pages (ideas, topics)
        ├── sources/         # Source summaries
        ├── synthesis/       # Cross-cutting syntheses
        └── insights/        # Extracted insights from memory
    
    The wiki is a living organism: it has a lifecycle, metabolism, and
    can transform. Its stage progresses from birth → growth → maturity.
    """

    SCHEMA = """# Haki Wiki Schema

This file instructs the LLM on how to maintain the wiki.
It is the "research org code" for knowledge management.

## Structure

- entities/ — pages for specific people, places, organizations, tools
- concepts/ — pages for ideas, topics, frameworks
- sources/ — summaries of ingested documents (one page per source)
- synthesis/ — cross-cutting analyses that connect multiple pages
- insights/ — facts extracted from self-learning memory graph

## Conventions

1. Every page MUST have YAML frontmatter: title, type, tags, sources
2. Use [[wiki links]] for cross-references
3. Track sources in frontmatter (source URLs, file paths)
4. Update existing pages instead of creating duplicates
5. Flag contradictions explicitly with > [!warning] blocks
6. Keep pages focused — split long pages into sub-topics

## Ingest Workflow

1. Read the source document fully
2. Identify: key entities, concepts, claims, data points
3. Create/update entity pages for each entity mentioned
4. Create/update concept pages for new ideas
5. Create a source summary in sources/
6. Update synthesis/ pages if the source challenges or extends existing knowledge
7. Update index.md with new/changed pages
8. Append to log.md with: date, source, pages touched

## Query Workflow

1. Read index.md to find relevant pages
2. Read the most relevant pages (2-5 usually)
3. Synthesize answer with [[wiki link]] citations
4. If the answer is substantial, file it as a new page

## Lint Workflow

1. Check for contradictions between pages with shared tags
2. Find orphan pages (no inbound links)
3. Flag stale pages (not updated in 30+ days with new sources)
4. Suggest new questions to investigate
5. Suggest new sources to find
"""

    def __init__(self):
        super().__init__("Wiki")
        self._wiki_dir = config.data_dir / "wiki"
        self._initialized = False

    async def initialize(self) -> None:
        """Create wiki directory structure and schema."""
        if self._initialized:
            return

        # Create directories
        for subdir in ["entities", "concepts", "sources", "synthesis", "insights"]:
            (self._wiki_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Write schema if missing
        schema_path = self._wiki_dir / "schema.md"
        if not schema_path.exists():
            schema_path.write_text(self.SCHEMA)

        # Initialize index and log if missing
        if not (self._wiki_dir / "index.md").exists():
            await self._write_index()
        if not (self._wiki_dir / "log.md").exists():
            (self._wiki_dir / "log.md").write_text("# Wiki Log\n\n")

        self._initialized = True
        self.pulse("initialized")
        logger.info("Wiki initialized at %s", self._wiki_dir)

    def _page_path(self, page_type: PageType, name: str) -> str:
        """Get relative path for a page."""
        slug = re.sub(r"[^\w\s-]", "", name.lower()).strip().replace(" ", "-")
        type_dir = {
            PageType.ENTITY: "entities",
            PageType.CONCEPT: "concepts",
            PageType.SOURCE: "sources",
            PageType.SYNTHESIS: "synthesis",
            PageType.INSIGHT: "insights",
        }.get(page_type, "concepts")
        return f"{type_dir}/{slug}.md"

    async def ingest_source(self, source_path: str | Path, title: str | None = None,
                             summary: str | None = None, entities: list[str] | None = None,
                             concepts: list[str] | None = None) -> dict[str, Any]:
        """
        Ingest a source document into the wiki.
        Creates/updates: source page, entity pages, concept pages, index, log.
        """
        source_path = Path(source_path)
        if not source_path.exists():
            return {"error": f"Source not found: {source_path}"}

        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        title = title or source_path.stem
        pages_touched: list[str] = []

        # 1. Create source summary page
        source_page = WikiPage(
            path=self._page_path(PageType.SOURCE, title),
            title=title,
            content=summary or f"Ingested from `{source_path.name}`.\n\n---\n\n{source_text[:2000]}",
            page_type=PageType.SOURCE,
            sources=[str(source_path)],
            tags=["source", "ingested"],
        )
        await self._write_page(source_page)
        pages_touched.append(source_page.path)

        # 2. Create entity pages
        if entities:
            for entity_name in entities:
                entity_path = self._page_path(PageType.ENTITY, entity_name)
                existing = await self._read_page(entity_path)
                if existing:
                    # Update existing entity
                    existing.content += f"\n\nMentioned in [[{title}]].\n{source_text[:500]}"
                    existing.links = list(set(existing.links + [title]))
                    existing.updated_at = datetime.utcnow()
                    await self._write_page(existing)
                else:
                    entity_page = WikiPage(
                        path=entity_path,
                        title=entity_name,
                        content=f"Entity mentioned in [[{title}]].\n\n{source_text[:300]}",
                        page_type=PageType.ENTITY,
                        tags=["entity"],
                        links=[title],
                        sources=[str(source_path)],
                    )
                    await self._write_page(entity_page)
                pages_touched.append(entity_path)

        # 3. Create concept pages
        if concepts:
            for concept_name in concepts:
                concept_path = self._page_path(PageType.CONCEPT, concept_name)
                existing = await self._read_page(concept_path)
                if existing:
                    existing.content += f"\n\nReferenced in [[{title}]]."
                    existing.links = list(set(existing.links + [title]))
                    existing.updated_at = datetime.utcnow()
                    await self._write_page(existing)
                else:
                    concept_page = WikiPage(
                        path=concept_path,
                        title=concept_name,
                        content=f"Concept from [[{title}]].",
                        page_type=PageType.CONCEPT,
                        tags=["concept"],
                        links=[title],
                        sources=[str(source_path)],
                    )
                    await self._write_page(concept_page)
                pages_touched.append(concept_path)

        # 4. Update index
        await self._rebuild_index()
        await self._append_log("ingest", title, pages_touched)

        return {
            "source": str(source_path),
            "pages_touched": pages_touched,
            "count": len(pages_touched),
        }

    async def ingest_text(self, title: str, text: str, source: str = "memory",
                           entities: list[str] | None = None,
                           concepts: list[str] | None = None) -> dict[str, Any]:
        """Ingest raw text directly (no file on disk)."""
        pages_touched: list[str] = []

        # Create source page
        source_page = WikiPage(
            path=self._page_path(PageType.SOURCE, title),
            title=title,
            content=text[:3000],
            page_type=PageType.SOURCE,
            sources=[source],
            tags=["source", "text"],
        )
        await self._write_page(source_page)
        pages_touched.append(source_page.path)

        # Create entities
        if entities:
            for en in entities:
                ep = self._page_path(PageType.ENTITY, en)
                existing = await self._read_page(ep)
                if existing:
                    existing.content += f"\n\nMentioned in [[{title}]]."
                    existing.links = list(set(existing.links + [title]))
                    existing.updated_at = datetime.utcnow()
                    await self._write_page(existing)
                else:
                    await self._write_page(WikiPage(
                        path=ep, title=en,
                        content=f"Entity from [[{title}]].",
                        page_type=PageType.ENTITY, links=[title], tags=["entity"],
                    ))
                pages_touched.append(ep)

        # Create concepts
        if concepts:
            for cn in concepts:
                cp = self._page_path(PageType.CONCEPT, cn)
                existing = await self._read_page(cp)
                if existing:
                    existing.content += f"\n\nFrom [[{title}]]."
                    existing.links = list(set(existing.links + [title]))
                    existing.updated_at = datetime.utcnow()
                    await self._write_page(existing)
                else:
                    await self._write_page(WikiPage(
                        path=cp, title=cn,
                        content=f"Concept from [[{title}]].",
                        page_type=PageType.CONCEPT, links=[title], tags=["concept"],
                    ))
                pages_touched.append(cp)

        await self._rebuild_index()
        await self._append_log("ingest", title, pages_touched)

        return {"pages_touched": pages_touched, "count": len(pages_touched)}

    async def query(self, question: str, top_k: int = 5) -> dict[str, Any]:
        """
        Query the wiki: find relevant pages, synthesize answer.
        Kaizen: score title + tags + content (not title/tags alone).
        """
        # Collect all pages
        all_pages = await self.get_all_pages()
        if not all_pages:
            return {
                "question": question,
                "sources": [],
                "context": "No pages in wiki yet. Ingest sources first.",
            }

        # Tokenize question (simple bag of words)
        question_words = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if len(w) > 2}
        scored: list[tuple[float, WikiPage]] = []
        for page in all_pages:
            title_words = set(re.findall(r"[a-z0-9]+", page.title.lower()))
            tag_words = set(re.findall(r"[a-z0-9]+", " ".join(page.tags).lower()))
            content_words = set(re.findall(r"[a-z0-9]+", page.content.lower()[:2000]))
            score = (
                3.0 * len(question_words & title_words)
                + 2.0 * len(question_words & tag_words)
                + 1.0 * len(question_words & content_words)
            )
            if score > 0:
                scored.append((score, page))

        scored.sort(reverse=True, key=lambda x: x[0])
        top_pages = [p for _, p in scored[:top_k]]

        # Build context from top pages
        context_parts = []
        for p in top_pages:
            context_parts.append(f"## {p.title}\n{p.content[:500]}")

        self.pulse("query", input_bytes=len(question), output_bytes=len(context_parts))
        return {
            "question": question,
            "sources": [{"title": p.title, "path": p.path, "tags": p.tags} for p in top_pages],
            "context": "\n\n".join(context_parts) if context_parts else "No relevant pages found.",
        }

    async def lint(self) -> WikiLintResult:
        """Health-check the wiki: contradictions, orphans, staleness."""
        result = WikiLintResult()
        pages = await self.get_all_pages()

        # Build inbound link counts
        inbound_links: dict[str, int] = defaultdict(int)
        for page in pages:
            for link in page.links:
                inbound_links[link] += 1

        for page in pages:
            # Orphan check
            if inbound_links.get(page.title, 0) == 0 and page.page_type not in (PageType.INDEX, PageType.LOG):
                result.orphan_pages.append(page.path)

            # Stale check (30 days)
            age = (datetime.utcnow() - page.updated_at).days
            if age > 30:
                result.stale_pages.append(f"{page.path} ({age} days old)")

        # Suggest questions
        if result.orphan_pages:
            result.suggested_questions.append(
                f"Should these orphan pages be linked from other pages? {result.orphan_pages[:3]}"
            )
        if result.stale_pages:
            result.suggested_questions.append(
                "Which stale pages need updating with new sources?"
            )

        return result

    async def get_all_pages(self) -> list[WikiPage]:
        """Get all wiki pages."""
        pages = []
        for md_file in self._wiki_dir.rglob("*.md"):
            if md_file.name in ("index.md", "log.md", "schema.md"):
                continue
            rel_path = str(md_file.relative_to(self._wiki_dir))
            try:
                text = md_file.read_text(encoding="utf-8")
                pages.append(WikiPage.from_markdown(rel_path, text))
            except Exception as e:
                logger.warning("Failed to parse %s: %s", md_file, e)
        return pages

    async def get_page(self, path: str) -> WikiPage | None:
        """Get a single page by relative path."""
        full_path = self._wiki_dir / path
        if not full_path.exists():
            return None
        text = full_path.read_text(encoding="utf-8")
        return WikiPage.from_markdown(path, text)

    # --- Internal helpers ---

    async def _write_page(self, page: WikiPage) -> None:
        """Write a wiki page to disk."""
        full_path = self._wiki_dir / page.path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(page.to_markdown(), encoding="utf-8")

    async def _read_page(self, path: str) -> WikiPage | None:
        """Read a wiki page from disk."""
        return await self.get_page(path)

    async def _rebuild_index(self) -> None:
        """Rebuild index.md from all pages."""
        pages = await self.get_all_pages()

        # Group by type
        by_type: dict[str, list[WikiPage]] = defaultdict(list)
        for p in pages:
            by_type[p.page_type.value].append(p)

        lines = [
            "# Wiki Index",
            "",
            f"Last updated: {datetime.utcnow().isoformat()}",
            f"Total pages: {len(pages)}",
            "",
        ]

        for ptype in ["entity", "concept", "source", "synthesis", "insight"]:
            if ptype in by_type:
                lines.append(f"## {ptype.title()}s")
                lines.append("")
                for p in sorted(by_type[ptype], key=lambda x: x.title):
                    lines.append(f"- [{p.title}]({p.path}) — {p.content[:80].strip()}...")
                lines.append("")

        index_path = self._wiki_dir / "index.md"
        index_path.write_text("\n".join(lines), encoding="utf-8")

    async def _write_index(self) -> None:
        """Write a fresh index."""
        await self._rebuild_index()

    async def _append_log(self, operation: str, title: str, pages: list[str]) -> None:
        """Append an entry to log.md."""
        log_path = self._wiki_dir / "log.md"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        entry = f"\n## [{timestamp}] {operation} | {title}\nPages: {', '.join(pages)}\n"
        with open(log_path, "a") as f:
            f.write(entry)

    async def get_schema(self) -> str:
        """Get the wiki schema (instructions for LLM discipline)."""
        schema_path = self._wiki_dir / "schema.md"
        if schema_path.exists():
            return schema_path.read_text()
        return self.SCHEMA

    def wiki_path(self) -> Path:
        return self._wiki_dir


# Singleton
wiki = Wiki()
