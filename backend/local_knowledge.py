"""Curated, immutable local Markdown knowledge snapshots and review inbox."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import time
import uuid
from contextlib import closing, contextmanager
from pathlib import Path

import yaml

from backend.external_knowledge import ExternalKnowledge, _connect_readonly, _digest, _words
from backend.knowledge import _clean_text

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_KNOWLEDGE_DIR = REPO_ROOT / "knowledge" / "local"
LOCAL_KNOWLEDGE_INDEX_DIR = REPO_ROOT / ".runtime" / "knowledge-local"
KNOWLEDGE_INBOX_DIR = REPO_ROOT / "knowledge" / "inbox"
LOCAL_INDEX_VERSION = 2
MAX_LOCAL_MARKDOWN_BYTES = 5 * 1024 * 1024
LOCAL_SOURCE = "local-curated"
LOCAL_ID_PREFIX = "local:"

_SENSITIVE = re.compile(
    r"(?i)\b[a-z][a-z0-9+.-]*://[^\s<>()]+|"
    r"\bbearer\s+\S+|"
    r"\b(?:[a-z0-9_.-]*(?:authorization|cookie|session(?:id)?|api[_-]?key|"
    r"access[_-]?key|password|passwd|secret|token)|flag|answer|candidate)\s*[:=]\s*[^\s,;]+|"
    r"\b(?:[\w.-]+)?\{[^\r\n{}]{1,512}\}|\bsk-[A-Za-z0-9_-]{12,}"
)


def normalized_keywords(query: str) -> str:
    """Stable, bounded query metadata for de-duplication and trace events."""
    return " ".join(_words(_SENSITIVE.sub(" ", query))[:32])[:240]


def redact_draft_text(value: object, *, known_flag: str = "") -> str:
    text = str(value or "")
    if known_flag:
        text = text.replace(known_flag, "[redacted]")
    text = _SENSITIVE.sub("[redacted]", text)
    return _clean_text(text, known_flag=known_flag)


def _is_link(path: Path) -> bool:
    """Include Windows junctions, which are not reported by is_symlink()."""
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


@contextmanager
def _index_lock(root: Path):
    """Serialize index publication and draft approval across processes."""
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".index.lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        deadline = time.monotonic() + 30
        while True:
            try:
                if os.name == "nt":
                    import msvcrt

                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Timed out waiting for local knowledge index lock") from exc
                time.sleep(0.1)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class LocalKnowledge(ExternalKnowledge):
    """Reuse the upstream FTS5 schema and ranking over a separate local source."""

    def __init__(self, root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR, snapshot_id: str = "") -> None:
        super().__init__(root, snapshot_id)

    @classmethod
    def index(cls, source_dir: str | Path = LOCAL_KNOWLEDGE_DIR,
              root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR) -> dict:
        root = Path(root).resolve()
        with _index_lock(root):
            return cls._index_locked(source_dir, root)

    @classmethod
    def _index_locked(cls, source_dir: str | Path, root: str | Path) -> dict:
        if _is_link(Path(source_dir)):
            raise ValueError("Local knowledge directory must not be a symlink or junction")
        source = Path(source_dir).resolve()
        root = Path(root).resolve()
        if not source.is_dir():
            raise ValueError(f"Local knowledge directory does not exist: {source}")
        files: list[tuple[str, Path, bytes]] = []
        skipped: list[tuple[str, str]] = []
        for path in sorted(source.rglob("*")):
            if not path.is_file() and not _is_link(path):
                continue
            rel = path.relative_to(source).as_posix()
            if _is_link(path) or any(_is_link(part) for part in path.parents if part != source):
                skipped.append((rel, "symbolic link ignored"))
                continue
            if path.suffix.lower() != ".md":
                skipped.append((rel, "non-Markdown file ignored"))
                continue
            raw = path.read_bytes()
            if len(raw) > MAX_LOCAL_MARKDOWN_BYTES or b"\0" in raw[:4096]:
                skipped.append((rel, "oversized or binary Markdown ignored"))
                continue
            try:
                raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                skipped.append((rel, "non-UTF-8 Markdown ignored"))
                continue
            files.append((rel, path, raw))
        digest = hashlib.sha256()
        digest.update(f"local-index-v{LOCAL_INDEX_VERSION}\n".encode())
        for rel, _, raw in files:
            digest.update(rel.encode("utf-8") + b"\0" + hashlib.sha256(raw).digest())
        for rel, reason in sorted(skipped):
            digest.update(b"\0diagnostic\0" + rel.encode("utf-8") + b"\0" + reason.encode("utf-8"))
        snapshot_id = f"local-v{LOCAL_INDEX_VERSION}-{digest.hexdigest()[:24]}"
        target = root / "snapshots" / snapshot_id
        root.mkdir(parents=True, exist_ok=True)
        if not (target / "index.sqlite3").is_file():
            building = root / (".building-" + uuid.uuid4().hex)
            staged = building / "source"
            try:
                staged.mkdir(parents=True)
                for rel, _, raw in files:
                    out = staged / rel
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(raw)
                cls._build(staged, building / "index.sqlite3", cls(root, "disabled"))
                if skipped:
                    db = sqlite3.connect(building / "index.sqlite3")
                    try:
                        db.executemany("INSERT INTO diagnostics VALUES (?, ?)", skipped)
                        db.commit()
                    finally:
                        db.close()
                target.parent.mkdir(parents=True, exist_ok=True)
                building.rename(target)
            finally:
                if building.exists():
                    shutil.rmtree(building)
        manifest = {"snapshot_id": snapshot_id, "index_version": LOCAL_INDEX_VERSION,
                    "source": LOCAL_SOURCE, "indexed_at": time.time()}
        temporary = root / (".current-" + uuid.uuid4().hex + ".json")
        temporary.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        temporary.replace(root / "current.json")
        return manifest

    def search(self, query: str, *, category: str = "", kind: str = "", limit: int = 5,
               expand: bool = True) -> list[dict]:
        out = []
        statuses: dict[str, str] = {}
        for hit in super().search(query, category=category, kind=kind, limit=limit, expand=expand):
            raw_id = hit["document_id"]
            if raw_id not in statuses:
                statuses[raw_id] = self._verification_status(raw_id)
            out.append({**hit, "document_id": LOCAL_ID_PREFIX + hit["document_id"],
                        "path": "knowledge/local/" + hit["path"],
                        "source": LOCAL_SOURCE, "source_url": "",
                        "verification_status": statuses[raw_id]})
        return out

    def _verification_status(self, document_id: str) -> str:
        """Read reviewed status from the hashed source copy in this snapshot."""
        with closing(_connect_readonly(self.snapshot / "index.sqlite3")) as db:
            doc = self._document(db, document_id)
            raw = (self.snapshot / "source" / doc["path"]).read_bytes()
            if _digest(raw) != doc["sha256"]:
                raise ValueError("Knowledge snapshot file hash mismatch")
        content = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        if not content.startswith("---\n") or "\n---\n" not in content[4:]:
            return "unknown"
        try:
            metadata = yaml.safe_load(content.split("\n---\n", 1)[0].removeprefix("---\n"))
        except yaml.YAMLError:
            return "unknown"
        status = metadata.get("verification_status") if isinstance(metadata, dict) else None
        return status if status in {"pending", "verified"} else "unknown"

    def read(self, document_id: str, *, start_line: int = 1, line_count: int = 120,
             char_offset: int = 0) -> dict:
        if not document_id.startswith(LOCAL_ID_PREFIX):
            raise ValueError("Not a local knowledge document ID")
        result = super().read(document_id.removeprefix(LOCAL_ID_PREFIX), start_line=start_line,
                              line_count=line_count, char_offset=char_offset)
        status = self._verification_status(document_id.removeprefix(LOCAL_ID_PREFIX))
        related = [{**item, "document_id": LOCAL_ID_PREFIX + item["document_id"],
                    "path": "knowledge/local/" + item["path"], "source": LOCAL_SOURCE}
                   for item in result["related_files"]]
        result.update(document_id=document_id, path="knowledge/local/" + result["path"],
                      source=LOCAL_SOURCE, verification_status=status, related_files=related)
        return result


def pin_local_snapshot(run_id: str, root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR) -> str:
    """Only call for a new run; absent manifests on resumed runs mean legacy behavior."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
        raise ValueError("Invalid run ID for local knowledge snapshot")
    root = Path(root).resolve()
    path = root / "runs" / (run_id + ".json")
    if path.exists():
        return str(json.loads(path.read_text(encoding="utf-8"))["snapshot_id"])
    snapshot_id = LocalKnowledge(root).snapshot_id
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps({"run_id": run_id, "snapshot_id": snapshot_id,
                                     "created_at": time.time()}), encoding="utf-8")
    temporary.replace(path)
    return snapshot_id


def local_snapshot_for_run(run_id: str, root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
        return ""
    path = Path(root).resolve() / "runs" / (run_id + ".json")
    if not path.is_file():
        return ""
    return str(json.loads(path.read_text(encoding="utf-8"))["snapshot_id"])


def write_verified_draft(meta, result, confirmation_source: str, *, run_id: str = "",
                         inbox_dir: str | Path | None = None) -> Path | None:
    """Create a review draft from a verified outcome without a model call."""
    if confirmation_source not in {"platform_confirmed", "independent_quorum"}:
        return None
    if confirmation_source == "independent_quorum" and (
        getattr(result, "status", "") != "verified" or len(set(getattr(result, "verified_by", ()))) < 2
    ):
        return None
    flag = str(getattr(result, "flag", "") or "")
    if not flag:
        return None
    summary = redact_draft_text(getattr(result, "findings_summary", ""), known_flag=flag)
    steps = [redact_draft_text(step, known_flag=flag)
             for step in getattr(result, "solution_steps", ())[:12]]
    steps = [step for step in steps if step]
    if len(summary) < 24 and not steps:
        return None
    title = redact_draft_text(getattr(meta, "name", "Unknown"), known_flag=flag)[:120]
    slug = re.sub(r"[^a-z0-9-]+", "-", title.lower()).strip("-")[:50] or "verified-method"
    key = _digest((run_id + "\0" + title + "\0" + summary).encode("utf-8"))[:12]
    path = Path(inbox_dir or KNOWLEDGE_INBOX_DIR) / f"{slug}-{key}.md"
    if path.exists():
        return path
    body = ["---", f"title: {json.dumps(title, ensure_ascii=False)}",
            f"source_challenge: {json.dumps(title, ensure_ascii=False)}",
            f"confirmation_source: {confirmation_source}", "verification_status: verified",
            f"run_id: {json.dumps(run_id)}", "---", "", f"# {title}", "",
            "## 可复用方法", "", summary or "参见下列验证步骤。", ""]
    if steps:
        body.extend(["## 验证步骤", ""])
        body.extend(f"{index}. {step}" for index, step in enumerate(steps, 1))
        body.append("")
    content = "\n".join(body)
    if _SENSITIVE.search(content):
        raise ValueError("Draft still contains sensitive material")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def approve_draft(draft: str | Path, *, inbox_dir: str | Path = KNOWLEDGE_INBOX_DIR,
                  source_dir: str | Path = LOCAL_KNOWLEDGE_DIR,
                  index_root: str | Path = LOCAL_KNOWLEDGE_INDEX_DIR) -> dict:
    inbox = Path(inbox_dir).resolve()
    candidate = Path(draft)
    raw_path = candidate if candidate.is_absolute() else inbox / candidate
    path = raw_path.resolve()
    try:
        rel = path.relative_to(inbox)
        raw_rel = raw_path.relative_to(inbox)
    except ValueError as exc:
        raise ValueError("Draft must be inside knowledge/inbox") from exc
    if any(inbox.joinpath(*raw_rel.parts[:index]).is_symlink()
           for index in range(1, len(raw_rel.parts) + 1)) or (
        path.suffix.lower() != ".md" or not path.is_file()
    ):
        raise ValueError("Draft must be a regular Markdown file in knowledge/inbox")
    raw = path.read_bytes()
    if len(raw) > MAX_LOCAL_MARKDOWN_BYTES or b"\0" in raw[:4096]:
        raise ValueError("Draft exceeds the Markdown size limit or contains binary data")
    content = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if _SENSITIVE.search(content):
        raise ValueError("Draft contains a flag, URL, credential, or session value")
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise ValueError("Draft is missing review metadata")
    metadata = yaml.safe_load(content.split("\n---\n", 1)[0].removeprefix("---\n"))
    if not isinstance(metadata, dict) or metadata.get("verification_status") != "verified" or (
        metadata.get("confirmation_source") not in {"platform_confirmed", "independent_quorum"}
    ) or not metadata.get("source_challenge"):
        raise ValueError("Draft lacks confirmed source and verification metadata")
    if _is_link(Path(source_dir)):
        raise ValueError("Local knowledge directory must not be a symlink or junction")
    source = Path(source_dir).resolve()
    destination = source / rel
    with _index_lock(Path(index_root).resolve()):
        if any(_is_link(source.joinpath(*rel.parts[:index]))
               for index in range(1, len(rel.parts) + 1)):
            raise ValueError("Curated document destination must not contain a symlink or junction")
        if destination.exists() or _is_link(destination):
            raise ValueError(f"Curated document already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        path.rename(destination)
        manifest = LocalKnowledge._index_locked(source, index_root)
    return {"path": destination.as_posix(), "snapshot_id": manifest["snapshot_id"]}
