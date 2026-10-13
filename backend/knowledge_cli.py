"""Manage and inspect the offline external CTF knowledge snapshot."""

from __future__ import annotations

import asyncio
import json
import sqlite3

import click

from backend.config import Settings
from backend.external_knowledge import ExternalKnowledge
from backend.knowledge import KnowledgeStore
from backend.knowledge_service import KnowledgeService
from backend.local_knowledge import LocalKnowledge, approve_draft


@click.group()
def main() -> None:
    """Sync, inspect and query the offline CTF knowledge index."""


def _root():
    return Settings().external_knowledge_dir


def _service() -> KnowledgeService:
    settings = Settings()
    memory = KnowledgeStore(settings.knowledge_db_path, enabled=settings.knowledge_enabled)
    service = KnowledgeService(settings, memory)
    service.external = ExternalKnowledge(settings.external_knowledge_dir)
    service.local = LocalKnowledge()
    return service


@main.command()
@click.option("--ref", default="main", help="Git branch, tag, or full commit SHA")
def sync(ref: str) -> None:
    """Download a Git revision and atomically publish a searchable snapshot."""
    try:
        result = ExternalKnowledge.sync(_root(), ref=ref)
    except Exception as exc:
        raise click.ClickException(f"Knowledge sync failed: {exc}") from exc
    click.echo(json.dumps(result, ensure_ascii=True, indent=2))


@main.command()
def status() -> None:
    """Show upstream and curated local snapshot counts."""
    click.echo(json.dumps({"external": ExternalKnowledge(_root()).status(),
                           "local": LocalKnowledge().status()}, ensure_ascii=True, indent=2))


@main.command("index-local")
def index_local() -> None:
    """Build the curated Markdown index without network access."""
    try:
        manifest = LocalKnowledge.index()
    except (OSError, ValueError, sqlite3.DatabaseError) as exc:
        raise click.ClickException(f"Local index failed: {exc}") from exc
    click.echo(json.dumps(manifest, ensure_ascii=True, indent=2))


@main.command()
@click.argument("draft")
def approve(draft: str) -> None:
    """Review an inbox Markdown draft into the curated corpus and reindex."""
    try:
        result = approve_draft(draft)
    except (OSError, ValueError, sqlite3.DatabaseError) as exc:
        raise click.ClickException(f"Approval failed: {exc}") from exc
    click.echo(json.dumps(result, ensure_ascii=True, indent=2))


@main.command()
@click.argument("query")
@click.option("--kind", default="", help="article, writeup, cheatsheet, tool, script, navigation")
@click.option("--limit", type=click.IntRange(1, 10), default=5)
def search(query: str, kind: str, limit: int) -> None:
    """Search upstream, curated local documents, and solving memory offline."""
    click.echo(json.dumps(_service().search(query, kind=kind, limit=limit),
                          ensure_ascii=True, indent=2))


@main.command()
@click.argument("document_id")
@click.option("--start-line", type=click.IntRange(min=1), default=1)
@click.option("--line-count", type=click.IntRange(1, 300), default=120)
def read(document_id: str, start_line: int, line_count: int) -> None:
    """Read original source lines from the current snapshot."""
    try:
        result = asyncio.run(_service().read_async(document_id, start_line=start_line,
                                                    line_count=line_count))
    except (ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, ensure_ascii=True, indent=2))
