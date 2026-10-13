"""Persistent challenge-package state and attachment bookkeeping."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CHALLENGE_STATES = {
    "discovered",
    "waiting_for_decision",
    "preparing",
    "waiting_for_package",
    "waiting_for_environment",
    "ready",
    "running",
    "solved",
    "needs_input",
    "failed",
}

ATTACHMENT_STATES = {"available", "selected", "downloading", "ready", "skipped", "failed"}


@dataclass(frozen=True)
class AttachmentCandidate:
    attachment_id: str
    name: str
    target: str = ""
    source_url: str = ""
    size: int | None = None
    metadata: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "attachment_id": self.attachment_id,
            "name": self.name,
            "target": self.target,
            "source_url": self.source_url,
            "size": self.size,
            "metadata": self.metadata or {},
        }


@dataclass(frozen=True)
class AttachmentArtifact:
    attachment_id: str
    name: str
    relative_path: str
    sha256: str
    bytes: int
    state: str = "ready"

    def as_dict(self) -> dict[str, Any]:
        return {
            "attachment_id": self.attachment_id,
            "name": self.name,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "bytes": self.bytes,
            "state": self.state,
        }


class ChallengeStateStore:
    """Small SQLite state store for one or more resumable CTF runs."""

    def __init__(self, path: str | Path, *, run_id: str | None = None) -> None:
        self.path = Path(path)
        self.run_id = run_id or uuid.uuid4().hex
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._ensure_run()

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
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL DEFAULT '',
                    origin TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'running',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS challenges (
                    run_id TEXT NOT NULL,
                    native_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    platform TEXT NOT NULL DEFAULT '',
                    mode TEXT NOT NULL DEFAULT 'unknown',
                    state TEXT NOT NULL DEFAULT 'discovered',
                    package_dir TEXT NOT NULL DEFAULT '',
                    connection_info TEXT NOT NULL DEFAULT '',
                    environment_json TEXT NOT NULL DEFAULT '{}',
                    reason TEXT NOT NULL DEFAULT '',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (run_id, native_id)
                );
                CREATE INDEX IF NOT EXISTS idx_challenges_run_state
                    ON challenges(run_id, state, updated_at);
                CREATE TABLE IF NOT EXISTS attachments (
                    run_id TEXT NOT NULL,
                    native_id TEXT NOT NULL,
                    attachment_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL DEFAULT '',
                    source_url TEXT NOT NULL DEFAULT '',
                    state TEXT NOT NULL DEFAULT 'available',
                    relative_path TEXT NOT NULL DEFAULT '',
                    sha256 TEXT NOT NULL DEFAULT '',
                    bytes INTEGER,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    reason TEXT NOT NULL DEFAULT '',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (run_id, native_id, attachment_id)
                );
                CREATE INDEX IF NOT EXISTS idx_attachments_state
                    ON attachments(run_id, native_id, state);
                """
            )

    def _ensure_run(self) -> None:
        now = time.time()
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT 1 FROM runs WHERE run_id=?", (self.run_id,)
            ).fetchone()
            connection.execute(
                """
                INSERT INTO runs(run_id, created_at, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET status='running', updated_at=excluded.updated_at
                """,
                (self.run_id, now, now),
            )
            if existing:
                connection.execute(
                    """
                    UPDATE challenges
                    SET state='waiting_for_package', reason='recovered after restart', updated_at=?
                    WHERE run_id=? AND state IN ('preparing', 'running')
                    """,
                    (now, self.run_id),
                )
                connection.execute(
                    """
                    UPDATE attachments
                    SET state='available', reason='recovered after restart', updated_at=?
                    WHERE run_id=? AND state IN ('downloading', 'selected')
                    """,
                    (now, self.run_id),
                )

    def close_run(self, status: str = "stopped") -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE runs SET status=?, updated_at=? WHERE run_id=?",
                (status, time.time(), self.run_id),
            )

    def upsert_challenge(
        self,
        *,
        native_id: str,
        name: str,
        slug: str,
        platform: str = "",
        mode: str = "unknown",
        package_dir: str = "",
        connection_info: str = "",
        environment: dict[str, Any] | None = None,
        state: str = "discovered",
        reason: str = "",
    ) -> None:
        if state not in CHALLENGE_STATES:
            raise ValueError(f"Unknown challenge state: {state}")
        now = time.time()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO challenges(
                    run_id, native_id, name, slug, platform, mode, state,
                    package_dir, connection_info, environment_json, reason,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, native_id) DO UPDATE SET
                    name=excluded.name,
                    slug=excluded.slug,
                    platform=excluded.platform,
                    mode=excluded.mode,
                    package_dir=excluded.package_dir,
                    connection_info=excluded.connection_info,
                    environment_json=excluded.environment_json,
                    state=excluded.state,
                    reason=excluded.reason,
                    updated_at=excluded.updated_at
                """,
                (
                    self.run_id,
                    str(native_id),
                    name,
                    slug,
                    platform,
                    mode,
                    state,
                    package_dir,
                    connection_info,
                    json.dumps(environment or {}, ensure_ascii=False, sort_keys=True),
                    reason,
                    now,
                    now,
                ),
            )

    def set_challenge_state(self, native_id: str, state: str, reason: str = "") -> None:
        if state not in CHALLENGE_STATES:
            raise ValueError(f"Unknown challenge state: {state}")
        with self._connect() as connection:
            connection.execute(
                "UPDATE challenges SET state=?, reason=?, updated_at=? WHERE run_id=? AND native_id=?",
                (state, reason, time.time(), self.run_id, str(native_id)),
            )

    def retry_challenge(self, native_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE challenges
                SET state='waiting_for_decision', reason='', updated_at=?
                WHERE run_id=? AND native_id=?
                """,
                (time.time(), self.run_id, str(native_id)),
            )
            connection.execute(
                """
                UPDATE attachments
                SET state='available', reason='', updated_at=?
                WHERE run_id=? AND native_id=? AND state != 'ready'
                """,
                (time.time(), self.run_id, str(native_id)),
            )

    def get_challenge(self, native_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM challenges WHERE run_id=? AND native_id=?",
                (self.run_id, str(native_id)),
            ).fetchone()
        if not row:
            return None
        result = dict(row)
        result["environment"] = json.loads(result.pop("environment_json") or "{}")
        return result

    def list_challenges(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM challenges WHERE run_id=? ORDER BY created_at",
                (self.run_id,),
            ).fetchall()
        return [self._row_to_challenge(row) for row in rows]

    @staticmethod
    def _row_to_challenge(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["environment"] = json.loads(result.pop("environment_json") or "{}")
        return result

    def upsert_attachment(self, native_id: str, candidate: AttachmentCandidate, *, state: str = "available") -> None:
        if state not in ATTACHMENT_STATES:
            raise ValueError(f"Unknown attachment state: {state}")
        now = time.time()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attachments(
                    run_id, native_id, attachment_id, name, target, source_url,
                    state, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, native_id, attachment_id) DO UPDATE SET
                    name=excluded.name,
                    target=excluded.target,
                    source_url=excluded.source_url,
                    metadata_json=excluded.metadata_json,
                    state=CASE
                        WHEN attachments.state IN ('ready', 'failed') THEN attachments.state
                        ELSE excluded.state
                    END,
                    updated_at=excluded.updated_at
                """,
                (
                    self.run_id,
                    str(native_id),
                    candidate.attachment_id,
                    candidate.name,
                    candidate.target,
                    candidate.source_url,
                    state,
                    json.dumps(candidate.metadata or {}, ensure_ascii=False, sort_keys=True),
                    now,
                    now,
                ),
            )

    def list_attachments(self, native_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM attachments WHERE run_id=? AND native_id=? ORDER BY created_at",
                (self.run_id, str(native_id)),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
            result.append(item)
        return result

    def set_attachment_state(
        self,
        native_id: str,
        attachment_id: str,
        state: str,
        *,
        relative_path: str = "",
        sha256: str = "",
        byte_count: int | None = None,
        reason: str = "",
        increment_attempts: bool = False,
    ) -> None:
        if state not in ATTACHMENT_STATES:
            raise ValueError(f"Unknown attachment state: {state}")
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE attachments SET
                    state=?, relative_path=COALESCE(NULLIF(?, ''), relative_path),
                    sha256=COALESCE(NULLIF(?, ''), sha256),
                    bytes=COALESCE(?, bytes), reason=?,
                    attempts=attempts + ?, updated_at=?
                WHERE run_id=? AND native_id=? AND attachment_id=?
                """,
                (
                    state,
                    relative_path,
                    sha256,
                    byte_count,
                    reason,
                    1 if increment_attempts else 0,
                    time.time(),
                    self.run_id,
                    str(native_id),
                    attachment_id,
                ),
            )

    def invalidate_attachment(self, native_id: str, attachment_id: str, reason: str) -> None:
        """Remove an untrusted ready artifact, including its stale path and digest."""
        with self._connect() as connection:
            connection.execute(
                """UPDATE attachments SET state='available', relative_path='', sha256='',
                   bytes=NULL, reason=?, updated_at=?
                   WHERE run_id=? AND native_id=? AND attachment_id=?""",
                (reason, time.time(), self.run_id, str(native_id), attachment_id),
            )

    def ready_artifacts(self, native_id: str) -> list[AttachmentArtifact]:
        return [
            AttachmentArtifact(
                attachment_id=row["attachment_id"],
                name=row["name"],
                relative_path=row["relative_path"],
                sha256=row["sha256"],
                bytes=int(row["bytes"] or 0),
                state=row["state"],
            )
            for row in self.list_attachments(native_id)
            if row["state"] == "ready" and row["relative_path"]
        ]

    @staticmethod
    def sha256_file(path: str | Path) -> tuple[str, int]:
        digest = hashlib.sha256()
        size = 0
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        return digest.hexdigest(), size
