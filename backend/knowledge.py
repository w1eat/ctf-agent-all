"""Persistent, redacted solving knowledge for retrieval-augmented CTF agents."""

from __future__ import annotations

import hashlib
import re
import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from backend.prompts import ChallengeMeta
from backend.solver_base import CANDIDATE_FOUND, FLAG_FOUND, GAVE_UP, VERIFIED, SolverResult

MAX_TEXT = 4000
DEFAULT_LIMIT = 6

_FLAG_PATTERNS = (
    re.compile(r"(?i)\b(?:flag|answer|token|candidate)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\b(?:[a-z0-9_.-]+)?\{[^\r\n{}]{1,512}\}"),
)
_SECRET_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[a-z0-9._~-]+"),
    re.compile(r"(?i)\b(?:api[_-]?key|password|passwd|secret|authorization|cookie)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)https?://[^\s/@]+:[^\s/@]+@"),
)
_COMMAND_NOISE = re.compile(r"(?im)^\s*(?:flag|candidate|answer|token)\s*[:=].*$")


@dataclass(frozen=True)
class KnowledgeQuery:
    name: str
    category: str = ""
    mode: str = ""
    description: str = ""
    tags: tuple[str, ...] = ()
    files: tuple[str, ...] = ()

    @classmethod
    def from_meta(cls, meta: ChallengeMeta) -> KnowledgeQuery:
        return cls(
            name=meta.name,
            category=meta.category,
            mode=meta.challenge_mode,
            description=meta.description,
            tags=tuple(meta.tags),
            files=(),
        )


@dataclass(frozen=True)
class KnowledgeRecord:
    challenge_name: str
    category: str
    mode: str
    method: str
    reasoning: str
    outcome: str
    source_model: str
    tags: tuple[str, ...] = ()
    digest: str = ""


def _clean_text(value: str, *, known_flag: str = "") -> str:
    text = str(value or "")
    if known_flag:
        text = text.replace(known_flag, "[redacted flag]")
    text = _COMMAND_NOISE.sub("", text)
    for pattern in _FLAG_PATTERNS + _SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    # Keep the knowledge store about techniques, not raw command transcripts.
    text = re.sub(r"(?im)^\s*(?:\$|#)\s+.*$", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_TEXT]


def _method_and_reasoning(summary: str, flag: str | None) -> tuple[str, str]:
    text = _clean_text(summary, known_flag=flag or "")
    if not text:
        return "", ""

    if text.lower().startswith("flag found via "):
        text = text[len("Flag found via "):].strip(" :")

    sentences = re.split(r"(?<=[.!?])\s+", text)
    method = sentences[0].strip()[:500] or "General challenge analysis"
    return method, text


def record_from_result(
    meta: ChallengeMeta,
    result: SolverResult,
    model_spec: str,
    *,
    confirmed: bool,
) -> KnowledgeRecord | None:
    """Convert a solver summary into safe, reusable knowledge."""
    if result.status not in (GAVE_UP, CANDIDATE_FOUND, FLAG_FOUND, VERIFIED) or not result.findings_summary:
        return None

    method, reasoning = _method_and_reasoning(result.findings_summary, result.flag)
    if len(reasoning) < 16:
        return None

    outcome = "accepted" if confirmed or result.status == VERIFIED else (
        "unverified_candidate" if result.status in {CANDIDATE_FOUND, FLAG_FOUND} else "incomplete"
    )
    return KnowledgeRecord(
        challenge_name=meta.name,
        category=meta.category,
        mode=meta.challenge_mode,
        method=method,
        reasoning=reasoning,
        outcome=outcome,
        source_model=model_spec,
        tags=tuple(meta.tags),
    )


class KnowledgeStore:
    """Small SQLite store with deterministic retrieval and duplicate suppression."""

    def __init__(self, path: str | Path, *, enabled: bool = True) -> None:
        self.path = Path(path)
        self.enabled = enabled
        self._lock = threading.RLock()
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    digest TEXT NOT NULL UNIQUE,
                    challenge_name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT '',
                    mode TEXT NOT NULL DEFAULT '',
                    tags TEXT NOT NULL DEFAULT '',
                    method TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    source_model TEXT NOT NULL DEFAULT '',
                    created_at REAL NOT NULL,
                    last_seen_at REAL NOT NULL,
                    seen_count INTEGER NOT NULL DEFAULT 1
                );
                CREATE INDEX IF NOT EXISTS idx_knowledge_category
                    ON knowledge_entries(category, outcome, last_seen_at DESC);
                CREATE INDEX IF NOT EXISTS idx_knowledge_name
                    ON knowledge_entries(challenge_name, last_seen_at DESC);
                """
            )

    @staticmethod
    def _digest(record: KnowledgeRecord) -> str:
        stable = "\x1f".join((record.category, record.mode, record.method, record.reasoning, record.outcome))
        return hashlib.sha256(stable.encode("utf-8")).hexdigest()

    def remember(self, record: KnowledgeRecord) -> bool:
        """Persist one entry. Returns True when a new row was inserted."""
        if not self.enabled:
            return False
        digest = self._digest(record)
        now = time.time()
        with self._lock, self._connect() as connection:
            existing = connection.execute(
                "SELECT 1 FROM knowledge_entries WHERE digest=?", (digest,)
            ).fetchone()
            if existing:
                connection.execute(
                    """
                    UPDATE knowledge_entries
                    SET last_seen_at=?, seen_count=seen_count + 1, source_model=?
                    WHERE digest=?
                    """,
                    (now, record.source_model[:200], digest),
                )
                return False
            connection.execute(
                """
                INSERT INTO knowledge_entries
                    (digest, challenge_name, category, mode, tags, method, reasoning,
                     outcome, source_model, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    digest,
                    record.challenge_name[:200],
                    record.category[:100],
                    record.mode[:50],
                    ",".join(record.tags)[:500],
                    record.method,
                    record.reasoning,
                    record.outcome[:50],
                    record.source_model[:200],
                    now,
                    now,
                ),
            )
            return True

    @staticmethod
    def _terms(query: KnowledgeQuery) -> list[str]:
        raw = " ".join(
            (query.name, query.category, query.mode, query.description, *query.tags, *query.files)
        )
        terms = []
        for term in re.findall(r"[a-zA-Z0-9_+#.-]{2,}|[\u4e00-\u9fff]{2,}", raw.lower()):
            if term not in terms:
                terms.append(term)
        return terms[:24]

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> KnowledgeRecord:
        return KnowledgeRecord(
            challenge_name=row["challenge_name"],
            category=row["category"],
            mode=row["mode"],
            method=row["method"],
            reasoning=row["reasoning"],
            outcome=row["outcome"],
            source_model=row["source_model"],
            tags=tuple(filter(None, row["tags"].split(","))),
            digest=row["digest"],
        )

    def get_by_digest(self, digest: str) -> KnowledgeRecord:
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid memory document ID")
        if not self.enabled:
            raise ValueError("Local memory is unavailable")
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM knowledge_entries WHERE digest=?", (digest,)).fetchone()
        if row is None:
            raise ValueError("Unknown memory document ID")
        return self._record_from_row(row)

    def search(self, query: KnowledgeQuery, limit: int = DEFAULT_LIMIT,
               outcomes: set[str] | None = None) -> list[KnowledgeRecord]:
        if not self.enabled or limit <= 0:
            return []
        if outcomes is not None and not outcomes:
            return []
        terms = self._terms(query)
        with self._lock, self._connect() as connection:
            if outcomes is None:
                rows = connection.execute("SELECT * FROM knowledge_entries").fetchall()
            else:
                placeholders = ",".join("?" for _ in outcomes)
                rows = connection.execute(
                    f"SELECT * FROM knowledge_entries WHERE outcome IN ({placeholders})",
                    tuple(sorted(outcomes)),
                ).fetchall()

        scored: list[tuple[int, sqlite3.Row]] = []
        query_name = query.name.lower()
        query_category = query.category.lower()
        for row in rows:
            searchable = " ".join(
                str(row[key]).lower()
                for key in ("challenge_name", "category", "mode", "tags", "method", "reasoning")
            )
            evidence_score = sum(1 for term in terms if term in searchable and term != query_category)
            if query_name and query_name in str(row["challenge_name"]).lower():
                evidence_score += 12
            if not evidence_score:
                continue
            score = evidence_score
            if query_category and query_category == str(row["category"]).lower():
                score += 8
            if query.mode and query.mode == row["mode"]:
                score += 2
            if row["outcome"] == "accepted":
                score += 2
            elif row["outcome"] in {"rejected", "rejected_candidate"}:
                score -= 3
            if score:
                scored.append((score, row))

        scored.sort(key=lambda item: (item[0], item[1]["last_seen_at"]), reverse=True)
        selected = scored[:limit]

        return [self._record_from_row(row) for _, row in selected]

    def render_context(self, query: KnowledgeQuery, limit: int = DEFAULT_LIMIT) -> str:
        records = self.search(query, limit=limit)
        if not records:
            return ""
        lines = [
            "Historical solving knowledge. Treat every item as an unverified hint; reproduce and verify it:",
        ]
        for index, record in enumerate(records, 1):
            lines.extend(
                [
                    f"{index}. [{record.outcome}] {record.method}",
                    f"   Reasoning: {record.reasoning}",
                ]
            )
        return "\n".join(lines)
