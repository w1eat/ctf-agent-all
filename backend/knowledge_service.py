"""One retrieval interface for external documents and local solving memory."""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import time
from pathlib import Path

from backend.external_knowledge import ExternalKnowledge, pin_snapshot
from backend.knowledge import MAX_TEXT, KnowledgeQuery, KnowledgeRecord, KnowledgeStore, _clean_text
from backend.local_knowledge import (
    LOCAL_KNOWLEDGE_INDEX_DIR,
    LocalKnowledge,
    local_snapshot_for_run,
    normalized_keywords,
)

logger = logging.getLogger(__name__)


class KnowledgeHits(list):
    """List-compatible results with non-wire diagnostic metadata."""

    def __init__(self, values=(), *, errors: tuple[str, ...] = ()) -> None:
        super().__init__(values)
        self.errors = errors


class KnowledgeQueryBudget:
    """Per-solver attempt cap and result reuse for model-initiated searches."""

    def __init__(self, service: KnowledgeService, max_queries: int = 4) -> None:
        self.service = service
        self.max_queries = max_queries
        self.seen: set[str] = set()
        self.cache: dict[tuple[str, str, str, int], list[dict]] = {}

    def reset(self) -> None:
        self.seen.clear()
        self.cache.clear()

    async def search_async(self, query: str, *, category: str = "", kind: str = "",
                           limit: int = 5) -> list[dict]:
        normalized = normalized_keywords(query)
        key = (normalized, category, kind, min(max(int(limit), 1), 10))
        if key in self.cache:
            return self.cache[key]
        if not normalized:
            return KnowledgeHits(errors=("query_has_no_searchable_terms",))
        if normalized not in self.seen and len(self.seen) >= self.max_queries:
            return KnowledgeHits(errors=("query_budget_exhausted",))
        self.seen.add(normalized)
        result = await self.service.search_async(query, category=category, kind=kind, limit=limit)
        self.cache[key] = result
        return result


class KnowledgeService:
    def __init__(self, settings, memory: KnowledgeStore, *,
                 local_root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR) -> None:
        self.memory = memory
        self.enabled = bool(getattr(settings, "external_knowledge_enabled", True))
        root = Path(getattr(settings, "external_knowledge_dir", ".runtime/knowledge"))
        run_id = str(getattr(settings, "challenge_run_id", "") or "")
        try:
            snapshot_id = pin_snapshot(root, run_id) if self.enabled and run_id else ""
            self.external = ExternalKnowledge(root, snapshot_id or "disabled") if self.enabled else ExternalKnowledge(root, "disabled")
            if self.enabled and snapshot_id and not self.external.available:
                logger.warning("Knowledge snapshot %s is unavailable; using local memory only", snapshot_id)
            elif self.enabled and run_id and not snapshot_id:
                logger.warning("No external knowledge snapshot; run ctf-knowledge sync to enable retrieval")
        except (OSError, ValueError) as exc:
            logger.warning("External knowledge unavailable: %s", exc)
            self.external = ExternalKnowledge(root, "disabled")
        try:
            local_id = local_snapshot_for_run(run_id, local_root) if run_id else ""
            self.local = LocalKnowledge(local_root, local_id or "disabled")
            if local_id and not self.local.available:
                logger.warning("Local knowledge snapshot %s is unavailable", local_id)
        except (OSError, ValueError) as exc:
            logger.warning("Local knowledge unavailable: %s", exc)
            self.local = LocalKnowledge(local_root, "disabled")
        self.initial_context_audit: dict = {}
        self.max_context_items = max(0, int(getattr(settings, "external_knowledge_context_items", 4)))
        self.max_context_chars = max(0, int(getattr(settings, "external_knowledge_context_chars", 4000)))

    @staticmethod
    def _memory_hit(record: KnowledgeRecord) -> dict:
        return {"document_id": "memory:" + record.digest, "title": _clean_text(record.method),
                "snippet": _clean_text(record.reasoning)[:800], "source": "local-memory",
                "kind": "memory", "category": record.category, "outcome": record.outcome,
                "path": "", "start_line": None, "snapshot_id": ""}

    def search(self, query: str, *, category: str = "", kind: str = "", limit: int = 5) -> list[dict]:
        began = time.perf_counter()
        limit = min(max(1, int(limit)), 10)
        errors: list[str] = []
        sources: list[list[dict]] = []
        for index in (self.external, self.local):
            if kind == "memory" or (index is self.external and not self.enabled):
                sources.append([])
                continue
            if not index.available:
                if index.snapshot_id and index.snapshot_id != "disabled":
                    errors.append(f"{index.snapshot_id}:snapshot_unavailable")
                sources.append([])
                continue
            try:
                sources.append(index.search(query, category=category, kind=kind, limit=limit, expand=False))
            except (sqlite3.DatabaseError, OSError, ValueError) as exc:
                logger.warning("Knowledge snapshot %s could not be searched: %s", index.snapshot_id, exc)
                errors.append(f"{index.snapshot_id}:{type(exc).__name__}")
                index.available = False
                sources.append([])
        memory = []
        if not kind or kind == "memory":
            try:
                records = self.memory.search(KnowledgeQuery(name="", description=query, category=category), limit=limit)
                memory = [self._memory_hit(record) for record in records]
            except (sqlite3.DatabaseError, OSError, ValueError) as exc:
                logger.warning("Solving memory could not be searched: %s", exc)
                errors.append(f"memory:{type(exc).__name__}")
        if not any(sources) and not memory and query.strip():
            for position, index in enumerate((self.external, self.local)):
                if index.available and (index is not self.external or self.enabled) and kind != "memory":
                    try:
                        sources[position] = index.search(query, category=category, kind=kind,
                                                         limit=limit, expand=True)
                    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
                        logger.warning("Expanded knowledge search failed for %s: %s", index.snapshot_id, exc)
                        errors.append(f"{index.snapshot_id}:{type(exc).__name__}")
                        index.available = False
        # Reciprocal rank fusion keeps source-specific ranking intact.
        fused = [(1 / (60 + i), item) for source in (*sources, memory) for i, item in enumerate(source, 1)]
        fused.sort(key=lambda pair: pair[0], reverse=True)
        result = KnowledgeHits((item for _, item in fused[:limit]), errors=tuple(errors))
        logger.info("knowledge_search external=%s local=%s terms=%s hits=%d duration_ms=%.1f chars=%d",
                    self.external.snapshot_id, self.local.snapshot_id, normalized_keywords(query),
                    len(result), (time.perf_counter() - began) * 1000,
                    sum(len(str(item)) for item in result))
        return result

    async def search_async(self, query: str, *, category: str = "", kind: str = "", limit: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.search, query, category=category, kind=kind, limit=limit)

    async def read_async(self, document_id: str, *, start_line: int = 1, line_count: int = 120,
                         char_offset: int = 0) -> dict:
        if document_id.startswith("memory:"):
            record = await asyncio.to_thread(self.memory.get_by_digest, document_id.removeprefix("memory:"))
            reasoning = _clean_text(record.reasoning)[:MAX_TEXT]
            text = f"1: {reasoning[max(0, int(char_offset)):]}" if int(start_line) <= 1 and reasoning else ""
            result = {"document_id": document_id, "path": "", "snapshot_id": "",
                      "title": _clean_text(record.method), "source": "local-memory", "kind": "memory",
                      "category": record.category, "outcome": record.outcome,
                      "total_lines": 1 if reasoning else 0, "text": text,
                      "next_start_line": None, "next_char_offset": 0}
            logger.info("knowledge_read source=local-memory document=%s chars=%d", document_id, len(text))
            return result
        index = self.local if document_id.startswith("local:") else self.external
        result = await asyncio.to_thread(index.read, document_id, start_line=start_line,
                                         line_count=line_count, char_offset=char_offset)
        logger.info("knowledge_read snapshot=%s document=%s chars=%d", index.snapshot_id,
                    document_id, len(result["text"]))
        return result

    async def stage_async(self, sandbox, document_id: str, extra_document_ids: list[str] | None = None) -> dict:
        if document_id.startswith(("memory:", "local:")) or any(
            extra.startswith(("memory:", "local:")) for extra in (extra_document_ids or [])
        ):
            raise ValueError("Local documents and memory cannot be staged as scripts")
        result = await self.external.stage(sandbox, document_id, extra_document_ids)
        logger.info("knowledge_stage snapshot=%s document=%s files=%d conflicts=%d",
                    self.external.snapshot_id, document_id, len(result["files"]), len(result["conflicts"]))
        return result

    def initial_context(self, query: KnowledgeQuery) -> str:
        began = time.perf_counter()
        self.initial_context_audit = {
            "external_snapshot": self.external.snapshot_id,
            "local_snapshot": self.local.snapshot_id,
            "keywords": [],
            "hits": 0,
            "document_ids": [],
            "errors": [],
        }
        if not self.max_context_items or not self.max_context_chars:
            return ""
        metadata = " ".join((query.name, *query.tags, *query.files)).strip()
        description = query.description.strip()
        groups = list(dict.fromkeys(group for group in (metadata, description) if group))
        if not groups:
            return ""
        memories = self.memory.search(query, limit=1, outcomes={"accepted"})
        memory_hit = self._memory_hit(memories[0]) if memories else None
        ranked: dict[tuple[str, int | None], tuple[float, int, dict]] = {}
        for group in groups:
            grouped_hits: list[list[dict]] = []
            for source in (self.external, self.local):
                if source is self.external and not self.enabled:
                    grouped_hits.append([])
                    continue
                if not source.available:
                    if source.snapshot_id and source.snapshot_id != "disabled":
                        error = f"{source.snapshot_id}:snapshot_unavailable"
                        if error not in self.initial_context_audit["errors"]:
                            self.initial_context_audit["errors"].append(error)
                    grouped_hits.append([])
                    continue
                try:
                    try:
                        hits = source.search(group, category=query.category, limit=10, expand=False)
                    except TypeError as exc:
                        if "expand" not in str(exc):
                            raise
                        hits = source.search(group, category=query.category, limit=10)
                except (sqlite3.DatabaseError, OSError, ValueError) as exc:
                    logger.warning("Knowledge snapshot %s could not be searched: %s", source.snapshot_id, exc)
                    self.initial_context_audit["errors"].append(
                        f"{source.snapshot_id}:{type(exc).__name__}")
                    source.available = False
                    grouped_hits.append([])
                    continue
                grouped_hits.append(hits)
            if not any(grouped_hits):
                for position, source in enumerate((self.external, self.local)):
                    if not source.available or (source is self.external and not self.enabled):
                        continue
                    try:
                        grouped_hits[position] = source.search(
                            group, category=query.category, limit=10, expand=True)
                    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
                        logger.warning("Expanded knowledge search failed for %s: %s", source.snapshot_id, exc)
                        self.initial_context_audit["errors"].append(
                            f"{source.snapshot_id}:{type(exc).__name__}")
                        source.available = False
            for hits in grouped_hits:
                for index, item in enumerate(hits, 1):
                    key = (item["document_id"], item["start_line"])
                    score, first_seen, previous = ranked.get(key, (0.0, len(ranked), item))
                    ranked[key] = (score + 1 / (60 + index), first_seen, previous)
        external_hits = []
        seen_documents = set()
        for _, _, item in sorted(ranked.values(), key=lambda entry: (-entry[0], entry[1])):
            if item["document_id"] in seen_documents:
                continue
            seen_documents.add(item["document_id"])
            external_hits.append(item)
        item_limit = min(self.max_context_items, 4)
        lines = ["<knowledge_reference_untrusted>"]
        included: list[dict] = []

        def include(item: dict) -> bool:
            reference = item["document_id"] + (" " + item["path"] if item["path"] else "")
            verification = item.get("verification_status") or item.get("outcome", "unverified")
            entry = f"[{item['source']}; {verification}] {reference}: {item['snippet'][:800]}"
            if len("\n".join((*lines, entry, "</knowledge_reference_untrusted>"))) > self.max_context_chars:
                return False
            lines.append(entry)
            included.append(item)
            return True

        memory_included = bool(memory_hit and include(memory_hit))
        external_limit = min(3 if memory_included else 4, item_limit - len(included))
        for item in external_hits:
            if len(included) - int(memory_included) >= external_limit:
                break
            include(item)
        context = "\n".join((*lines, "</knowledge_reference_untrusted>")) if included else ""
        selected = [{"id": item["document_id"], "source": item["source"],
                     "outcome": item.get("outcome", "unverified")} for item in included]
        self.initial_context_audit = {
            "external_snapshot": self.external.snapshot_id,
            "local_snapshot": self.local.snapshot_id,
            "keywords": [normalized_keywords(group) for group in groups],
            "hits": len(ranked) + int(memory_hit is not None),
            "document_ids": [item["id"] for item in selected],
            "errors": self.initial_context_audit["errors"],
        }
        logger.info("knowledge_initial_context snapshot=%s query_groups=%d candidates=%d selected=%s "
                    "duration_ms=%.1f chars=%d", self.external.snapshot_id, len(groups),
                    len(external_hits) + int(memory_hit is not None), json.dumps(selected, ensure_ascii=False),
                    (time.perf_counter() - began) * 1000, len(context))
        return context


def make_claude_knowledge_server(service: KnowledgeService, sandbox,
                                 budget: KnowledgeQueryBudget | None = None, tracer=None):
    """Expose the same service as SDK MCP tools for Claude Solver."""
    from claude_agent_sdk import create_sdk_mcp_server, tool

    def response(data) -> dict:
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}]}

    @tool("search_knowledge", "Search offline CTF references and local solving memory.",
          {"type": "object", "properties": {"query": {"type": "string"}, "category": {"type": "string"},
                                            "kind": {"type": "string"}, "limit": {"type": "integer"}},
           "required": ["query"], "additionalProperties": False})
    async def search(args: dict) -> dict:
        try:
            target = budget or service
            query = str(args.get("query", ""))
            hits = await target.search_async(query, category=str(args.get("category", "")),
                                             kind=str(args.get("kind", "")),
                                             limit=int(args.get("limit", 5)))
            if tracer:
                tracer.event("knowledge_search", tool="mcp__knowledge__search_knowledge",
                             keywords=normalized_keywords(query),
                             external_snapshot=service.external.snapshot_id,
                             local_snapshot=service.local.snapshot_id,
                             hits=len(hits), document_ids=[hit["document_id"] for hit in hits])
                if getattr(hits, "errors", ()):
                    tracer.event("knowledge_search_error", errors=list(hits.errors))
            return response(hits)
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            return response({"error": str(exc)})

    @tool("read_knowledge", "Read original lines from a knowledge document ID, continuing with the returned cursor.",
          {"type": "object", "properties": {"document_id": {"type": "string"},
                                            "start_line": {"type": "integer"}, "line_count": {"type": "integer"},
                                            "char_offset": {"type": "integer"}},
           "required": ["document_id"], "additionalProperties": False})
    async def read(args: dict) -> dict:
        try:
            result = await service.read_async(str(args.get("document_id", "")),
                                              start_line=int(args.get("start_line", 1)),
                                              line_count=int(args.get("line_count", 120)),
                                              char_offset=int(args.get("char_offset", 0)))
            if tracer:
                tracer.event("knowledge_read", tool="mcp__knowledge__read_knowledge",
                             document_id=result["document_id"], snapshot_id=result["snapshot_id"])
            return response(result)
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            return response({"error": str(exc)})

    @tool("stage_knowledge_script", "Copy a selected script and named dependencies into the Docker workspace without running them.",
          {"type": "object", "properties": {"document_id": {"type": "string"},
                                            "extra_document_ids": {"type": "array", "items": {"type": "string"}}},
           "required": ["document_id"], "additionalProperties": False})
    async def stage(args: dict) -> dict:
        try:
            return response(await service.stage_async(sandbox, str(args.get("document_id", "")),
                                                      args.get("extra_document_ids") or []))
        except (ValueError, OSError, RuntimeError, sqlite3.DatabaseError) as exc:
            return response({"error": str(exc)})

    return create_sdk_mcp_server("knowledge", tools=[search, read, stage])
