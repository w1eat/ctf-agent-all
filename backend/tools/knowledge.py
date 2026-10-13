"""Model-facing wrappers over the shared knowledge service."""

from __future__ import annotations

import json
import sqlite3

from pydantic_ai import RunContext

from backend.deps import SolverDeps

KNOWLEDGE_TOOL_SPECS = [
    {"name": "search_knowledge", "description": "Search offline CTF articles, writeups, scripts and local solving memory.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"},
                     "category": {"type": "string"}, "kind": {"type": "string"}, "limit": {"type": "integer"}},
                     "required": ["query"]}},
    {"name": "read_knowledge", "description": "Read original source lines using a search result document ID; follow its continuation cursor.",
     "inputSchema": {"type": "object", "properties": {"document_id": {"type": "string"},
                     "start_line": {"type": "integer"}, "line_count": {"type": "integer"},
                     "char_offset": {"type": "integer"}}, "required": ["document_id"]}},
    {"name": "stage_knowledge_script", "description": "Copy one selected source script and explicitly named dependencies into the Docker workspace; does not execute them.",
     "inputSchema": {"type": "object", "properties": {"document_id": {"type": "string"},
                     "extra_document_ids": {"type": "array", "items": {"type": "string"}}},
                     "required": ["document_id"]}},
]


async def search_knowledge(ctx: RunContext[SolverDeps], query: str, category: str = "",
                           kind: str = "", limit: int = 5) -> str:
    """Search CTF articles, writeups, scripts and local solving memory."""
    service = getattr(ctx.deps, "knowledge_query_budget", None) or ctx.deps.knowledge_service
    if service is None:
        return "Knowledge search is unavailable."
    hits = await service.search_async(query, category=category, kind=kind, limit=limit)
    tracer = getattr(ctx.deps, "knowledge_tracer", None)
    if tracer and getattr(hits, "errors", ()):
        tracer.event("knowledge_search_error", errors=list(hits.errors))
    return json.dumps(hits, ensure_ascii=False)


async def read_knowledge(ctx: RunContext[SolverDeps], document_id: str, start_line: int = 1,
                         line_count: int = 120, char_offset: int = 0) -> str:
    """Read source lines of one result; use the returned cursor for continuation."""
    service = ctx.deps.knowledge_service
    if service is None:
        return "Knowledge reading is unavailable."
    try:
        result = await service.read_async(document_id, start_line=start_line, line_count=line_count,
                                          char_offset=char_offset)
        return json.dumps(result, ensure_ascii=False)
    except (ValueError, OSError, sqlite3.DatabaseError) as exc:
        return f"Knowledge read failed: {exc}"


async def stage_knowledge_script(ctx: RunContext[SolverDeps], document_id: str,
                                 extra_document_ids: list[str] | None = None) -> str:
    """Copy a selected knowledge script and explicit dependencies into the Docker workspace."""
    service = ctx.deps.knowledge_service
    if service is None:
        return "Knowledge script staging is unavailable."
    try:
        result = await service.stage_async(ctx.deps.sandbox, document_id, extra_document_ids)
        return json.dumps(result, ensure_ascii=False)
    except (ValueError, OSError, RuntimeError, sqlite3.DatabaseError) as exc:
        return f"Knowledge script staging failed: {exc}"
