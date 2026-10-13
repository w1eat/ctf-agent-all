"""Versioned, offline search over the Des-CTF-Knowledge repository."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import posixpath
import re
import shutil
import sqlite3
import subprocess
import time
import uuid
from contextlib import closing
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

SOURCE_URL = "https://github.com/Dest1ny-Sec/Des-CTF-Knowledge.git"
INDEX_VERSION = 5
MAX_RESULT_COUNT = 10
MAX_READ_LINES = 300
MAX_READ_CHARS = 24_000
MAX_STAGE_FILES = 100
MAX_STAGE_BYTES = 20 * 1024 * 1024
logger = logging.getLogger(__name__)

_WORDS = re.compile(r"[a-zA-Z0-9_+#.://=-]{2,}|[\u4e00-\u9fff]+")
_HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_ALIASES = {
    "php反序列化": "deserialization 反序列化 wakeup",
    "图片宽高": "png dimensions ihdr crc 宽高",
    "命令执行": "rce command injection system exec",
    "文件包含": "lfi include php filter",
    "文件上传": "upload htaccess mime",
    "sql注入": "sqli sql injection 注入",
    "postgresql": "postgres pgsql pg_database 数据库",
    "postgres": "postgresql pgsql pg_database 数据库",
    "pgsql": "postgresql postgres pg_database 数据库",
    "布尔盲注": "boolean blind sql injection oracle 布尔注入",
    "布尔注入": "boolean blind sql injection oracle 布尔盲注",
    "boolean blind": "布尔盲注 布尔注入 oracle",
    "server-side program": "copy to program copy from program pg_execute_server_program",
    "copy to program": "server-side program pg_execute_server_program 退出状态",
    "copy from program": "server-side program pg_execute_server_program",
}
_COPY_PROGRAM_VARIANT = re.compile(
    r"\bcopy\s*(?:(?:from\s*/\s*to)|(?:(?:\.{3}|…)\s*to))\s+program\b"
)
_SCRIPT_SUFFIXES = {".py", ".sh", ".pl", ".rb", ".js", ".php", ".sage", ".c", ".cpp", ".java"}
_TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".pl", ".rb", ".js", ".php", ".sage", ".c", ".cpp", ".java", ".json", ".yml", ".yaml", ".toml", ".ini", ".xml", ".html", ".sql", ".csv"}
_SKIP_DIRS = {".git", "__pycache__", ".github", "node_modules", ".venv"}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _words(value: str, *, expand: bool = False) -> list[str]:
    value = value.lower()
    if expand:
        aliases = [extra for key, extra in _ALIASES.items() if key in value]
        if _COPY_PROGRAM_VARIANT.search(value):
            aliases.append("copy to program copy from program server-side program pg_execute_server_program")
        value += " " + " ".join(aliases)
    tokens: list[str] = []
    for match in _WORDS.finditer(value):
        word = match.group()
        if "\u4e00" <= word[0] <= "\u9fff":
            tokens.extend(word[i:i + 2] for i in range(len(word) - 1))
            if len(word) == 1:
                tokens.append(word)
        else:
            tokens.append(word)
            tokens.extend(part for part in re.split(r"[^a-z0-9]+", word) if len(part) > 1)
    return list(dict.fromkeys(tokens))


def _indexed(value: str) -> str:
    return " ".join(_words(value))


def _snippet_near_match(body: str, terms: list[str], width: int = 800,
                        fallback_terms: list[str] | None = None) -> str:
    """Use original source text around a query term, falling back to aliases."""
    lowered = body.casefold()
    positions = [lowered.find(term.casefold()) for term in terms if len(term) >= 2]
    positions = [pos for pos in positions if pos >= 0]
    if not positions and fallback_terms:
        positions = [lowered.find(term.casefold()) for term in fallback_terms if len(term) >= 2]
        positions = [pos for pos in positions if pos >= 0]
    if not positions or len(body) <= width:
        return body[:width]
    start = max(0, min(positions) - 180)
    return body[start:start + width]


def _kind(path: str, content: str | None = None) -> str:
    name = PurePosixPath(path).name.lower()
    if name in {"ai-search-index.md", "readme.md"} or name.endswith(".idx.md") or name == "scripts-index.md":
        return "navigation"
    if name == "payload-cheatsheet.md":
        return "cheatsheet"
    if path.startswith("CTF大赛WP集合/") or path.startswith("WP汇总/"):
        return "writeup"
    if path.startswith("工具使用/"):
        return "tool"
    if path.startswith("CTF常用脚本及工具/"):
        if not PurePosixPath(path).suffix and content and content.lstrip().startswith(("#!", "import ", "from ", "<?php")):
            return "script"
        return "script" if PurePosixPath(path).suffix.lower() in _SCRIPT_SUFFIXES else "tool"
    return "article"


def _category(path: str, title: str) -> str:
    text = (path + " " + title).lower()
    for category, markers in {
        "web": ("web", "sql", "ssrf", "ssti", "php", "xss", "jwt", "文件上传", "文件包含", "反序列化", "命令执行"),
        "pwn": ("pwn", "rop", "heap", "堆利用", "栈溢出"),
        "reverse": ("reverse", "逆向", "reversing", "ida", "jadx"),
        "crypto": ("crypto", "rsa", "aes", "密码", "加密"),
        "misc": ("misc", "隐写", "流量", "取证", "压缩包", "png", "音频"),
    }.items():
        if any(marker in text for marker in markers):
            return category
    return ""


def _text_file(path: Path) -> tuple[str | None, bytes]:
    raw = path.read_bytes()
    if len(raw) > 5 * 1024 * 1024 or b"\0" in raw[:4096]:
        return None, raw
    if path.suffix.lower() not in _TEXT_SUFFIXES and path.suffix:
        return None, raw
    try:
        return raw.decode("utf-8-sig"), raw
    except UnicodeDecodeError:
        return None, raw


def _provenance(content: str | None) -> tuple[str, str, str]:
    if not content:
        return "", "", ""
    head = "\n".join(content.splitlines()[:35])
    author_match = re.search(r"(?im)^\s*(?:作者|author)\s*[:：]\s*(.{1,100})$", head)
    url_match = re.search(r"(?im)^\s*(?:原文|原文链接|来源|source)\s*[:：]\s*(?:\[.*?\]\()?\s*(https?://[^\s)]+)", head)
    license_match = re.search(r"(?im)^\s*(?:许可|license)\s*[:：]\s*(.{1,100})$", head)
    return (author_match.group(1).strip() if author_match else "",
            url_match.group(1).strip() if url_match else "",
            license_match.group(1).strip() if license_match else "")


def _navigation_tags(source: Path) -> dict[str, str]:
    """Attach explicit navigation headings and keywords to linked source files."""
    labels: dict[str, set[str]] = {}
    script_root = source / "CTF常用脚本及工具"
    script_paths = [path.relative_to(source).as_posix() for path in script_root.rglob("*") if path.is_file()] if script_root.is_dir() else []
    for index_path in (source / "AI-SEARCH-INDEX.md", source / "CTF常用脚本及工具" / "SCRIPTS-INDEX.md"):
        if not index_path.is_file():
            continue
        blocks = re.split(r"(?=^###\s+)", index_path.read_text(encoding="utf-8-sig"), flags=re.MULTILINE)
        for block in blocks:
            heading = _HEAD.match(block.splitlines()[0]) if block.splitlines() else None
            if not heading:
                continue
            terms = {heading.group(2).strip()}
            for line in block.splitlines():
                if "关键词" in line or "适用场景" in line:
                    terms.update(re.findall(r"`([^`]{2,60})`", line))
            for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", block):
                if "://" in link:
                    continue
                rel = posixpath.normpath(posixpath.join(index_path.parent.relative_to(source).as_posix(), unquote(link)))
                if not rel.startswith("../") and (source / rel).is_file():
                    labels.setdefault(rel, set()).update(terms)
            if index_path.name == "SCRIPTS-INDEX.md":
                directory = re.search(r"`([^`]+/)`", heading.group(2))
                if directory:
                    prefix = posixpath.normpath("CTF常用脚本及工具/" + directory.group(1)) + "/"
                    for path in script_paths:
                        if path.startswith(prefix):
                            labels.setdefault(path, set()).update(terms)
    return {path: " ".join(sorted(items))[:500] for path, items in labels.items()}


def _chunks(content: str, path: str):
    """Yield heading/paragraph chunks while preserving source line positions."""
    lines = content.splitlines()
    headings: list[str] = []
    start = 1
    fence = False
    for pos, line in enumerate(lines, 1):
        heading = _HEAD.match(line) if path.endswith(".md") and not fence else None
        if heading and pos > start:
            yield start, pos - 1, " / ".join(headings), "\n".join(lines[start - 1:pos - 1])
            start = pos
        if heading:
            level = len(heading.group(1))
            headings = headings[:level - 1] + [heading.group(2)]
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        # Split only at paragraph boundaries, never inside a code fence or table.
        size = sum(map(len, lines[start - 1:pos]))
        if not line.strip() and pos > start and size >= 3000 and (not fence or size >= 6000 and pos - start > 100):
            yield start, pos, " / ".join(headings), "\n".join(lines[start - 1:pos])
            start = pos + 1
    if start <= len(lines):
        yield start, len(lines), " / ".join(headings), "\n".join(lines[start - 1:])


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def _row_tags(row: sqlite3.Row) -> str:
    try:
        return row["tags"]
    except IndexError:
        return ""


class ExternalKnowledge:
    def __init__(self, root: str | Path, snapshot_id: str = "") -> None:
        self.root = Path(root).resolve()
        self.snapshot_id = snapshot_id or self.current_id()
        self.snapshot = self.root / "snapshots" / self.snapshot_id if self.snapshot_id else None
        self.available = bool(self.snapshot and (self.snapshot / "index.sqlite3").is_file())
        self._cache: dict[tuple[str, str, str, int], list[dict]] = {}

    def current_id(self) -> str:
        path = self.root / "current.json"
        try:
            return str(json.loads(path.read_text(encoding="utf-8"))["snapshot_id"])
        except (OSError, ValueError, KeyError):
            return ""

    @staticmethod
    def _git(args: list[str], *, cwd: Path | None = None) -> str:
        result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, timeout=600)
        return result.stdout.strip()

    @classmethod
    def sync(cls, root: str | Path, *, ref: str = "main", source_url: str = SOURCE_URL) -> dict:
        root = Path(root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        known_commit = ref.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", ref) else ""
        if ref == "main":
            remote_head = cls._git(["ls-remote", "--heads", source_url, ref])
            known_commit = remote_head.split()[0] if remote_head else ""
        if known_commit and (root / "snapshots" / f"{known_commit}-v{INDEX_VERSION}" / "index.sqlite3").is_file():
            return cls._publish_current(root, known_commit, source_url)
        building = root / (".building-" + uuid.uuid4().hex)
        repo = building / "source"
        previous = cls(root)
        try:
            building.mkdir()
            if re.fullmatch(r"[0-9a-fA-F]{40}", ref):
                cls._git(["init", str(repo)])
                cls._git(["remote", "add", "origin", source_url], cwd=repo)
                cls._git(["fetch", "--depth=1", "origin", ref], cwd=repo)
                cls._git(["checkout", "--detach", "FETCH_HEAD"], cwd=repo)
            else:
                cls._git(["clone", "--depth=1", "--branch", ref, source_url, str(repo)])
            commit = cls._git(["rev-parse", "HEAD"], cwd=repo)
            snapshot_id = f"{commit}-v{INDEX_VERSION}"
            target = root / "snapshots" / snapshot_id
            if not target.is_dir():
                cls._build(repo, building / "index.sqlite3", previous)
                target.parent.mkdir(parents=True, exist_ok=True)
                building.rename(target)
            return cls._publish_current(root, commit, source_url)
        finally:
            if building.exists():
                shutil.rmtree(building)

    @staticmethod
    def _publish_current(root: Path, commit: str, source_url: str) -> dict:
        manifest = {"snapshot_id": f"{commit}-v{INDEX_VERSION}", "commit": commit,
                    "source_url": source_url, "index_version": INDEX_VERSION, "synced_at": time.time()}
        current_temp = root / (".current-" + uuid.uuid4().hex + ".json")
        current_temp.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        current_temp.replace(root / "current.json")
        return manifest

    @classmethod
    def _build(cls, source: Path, db_path: Path, previous: ExternalKnowledge) -> None:
        connection = sqlite3.connect(db_path)
        try:
            connection.executescript("""
                CREATE TABLE documents (id TEXT PRIMARY KEY, path TEXT NOT NULL UNIQUE, kind TEXT NOT NULL,
                    category TEXT NOT NULL, title TEXT NOT NULL, tags TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
                    text_available INTEGER NOT NULL, author TEXT NOT NULL DEFAULT '', original_url TEXT NOT NULL DEFAULT '',
                    license TEXT NOT NULL DEFAULT '');
                CREATE TABLE chunks (id INTEGER PRIMARY KEY, document_id TEXT NOT NULL, start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL, heading TEXT NOT NULL, body TEXT NOT NULL, sha256 TEXT NOT NULL);
                CREATE VIRTUAL TABLE chunk_fts USING fts5(title, tags, path, body, tokenize='unicode61');
                CREATE TABLE diagnostics (path TEXT NOT NULL, detail TEXT NOT NULL);
                CREATE INDEX idx_chunks_document ON chunks(document_id, start_line);
            """)
            old = _connect_readonly(previous.snapshot / "index.sqlite3") if previous.available else None
            try:
                files = sorted(p for p in source.rglob("*") if p.is_file() and not any(part in _SKIP_DIRS for part in p.relative_to(source).parts))
                nav_tags = _navigation_tags(source)
                for path in files:
                    rel = path.relative_to(source).as_posix()
                    if path.is_symlink():
                        connection.execute("INSERT INTO diagnostics VALUES (?, ?)", (rel, "symbolic link ignored"))
                        continue
                    content, raw = _text_file(path)
                    doc_id = _digest(rel.encode("utf-8"))[:24]
                    title = next((m.group(2) for line in (content or "").splitlines()[:30] if (m := _HEAD.match(line))), path.stem)
                    kind = _kind(rel, content)
                    category = _category(rel, title)
                    tags = nav_tags.get(rel, "")
                    sha = _digest(raw)
                    author, original_url, license_name = _provenance(content)
                    connection.execute("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                       (doc_id, rel, kind, category, title, tags, sha, len(raw),
                                        int(content is not None), author, original_url, license_name))
                    if content is None:
                        continue
                    cached = old.execute("SELECT sha256 FROM documents WHERE id=?", (doc_id,)).fetchone() if old else None
                    sections = ([(r["start_line"], r["end_line"], r["heading"], r["body"]) for r in old.execute("SELECT * FROM chunks WHERE document_id=? ORDER BY start_line", (doc_id,))]
                                if cached and cached["sha256"] == sha else _chunks(content, rel))
                    for start, end, heading, body in sections:
                        if not body.strip():
                            continue
                        cursor = connection.execute("INSERT INTO chunks(document_id,start_line,end_line,heading,body,sha256) VALUES (?,?,?,?,?,?)",
                                                    (doc_id, start, end, heading, body, _digest(body.encode("utf-8"))))
                        connection.execute("INSERT INTO chunk_fts(rowid,title,tags,path,body) VALUES (?,?,?,?,?)",
                                           (cursor.lastrowid, _indexed(title + " " + heading), _indexed(category + " " + kind + " " + tags), _indexed(rel), _indexed(body)))
                    if rel.endswith(".md"):
                        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", content):
                            if "://" not in target and not (path.parent / target).exists():
                                connection.execute("INSERT INTO diagnostics VALUES (?, ?)", (rel, f"missing link: {target[:200]}"))
                connection.commit()
            finally:
                if old:
                    old.close()
        finally:
            connection.close()

    def status(self) -> dict:
        result = {"available": self.available, "snapshot_id": self.snapshot_id}
        if self.available:
            with closing(_connect_readonly(self.snapshot / "index.sqlite3")) as db, db:
                result.update(documents=db.execute("SELECT count(*) FROM documents").fetchone()[0],
                              chunks=db.execute("SELECT count(*) FROM chunks").fetchone()[0],
                              diagnostics=db.execute("SELECT count(*) FROM diagnostics").fetchone()[0])
        return result

    def _document(self, db: sqlite3.Connection, document_id: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if row is None:
            raise ValueError("Unknown document ID for this knowledge snapshot")
        return row

    def search(self, query: str, *, category: str = "", kind: str = "", limit: int = 5,
               expand: bool = True) -> list[dict]:
        if not self.available or not query.strip():
            return []
        limit = min(max(int(limit), 1), MAX_RESULT_COUNT)
        key = (query, category, kind, limit, expand)
        if key in self._cache:
            return self._cache[key]
        base_terms = _words(query)
        if not base_terms:
            return []
        expanded_terms = _words(query, expand=expand)
        if len(base_terms) <= 32:
            windows = [base_terms]
        else:
            window_count = min(6, math.ceil(len(base_terms) / 16))
            last_start = len(base_terms) - 16
            starts = [round(index * last_start / (window_count - 1)) for index in range(window_count)]
            windows = [base_terms[start:start + 16] for start in starts]
        base_set = set(base_terms)
        aliases = [term for term in expanded_terms if term not in base_set]
        query_groups = [list(dict.fromkeys((*window, *aliases)))[:32] for window in windows]
        searched_terms = {term for group in query_groups for term in group}
        rows_by_chunk: dict[int, sqlite3.Row] = {}
        with closing(_connect_readonly(self.snapshot / "index.sqlite3")) as db, db:
            for group in query_groups:
                match = " OR ".join('"' + term.replace('"', '""') + '"' for term in group)
                sql = """SELECT d.*, c.id AS chunk_id, c.start_line, c.end_line,
                           c.heading, c.body, c.sha256 AS chunk_hash,
                           bm25(chunk_fts, 5.0, 4.0, 2.0, 1.0) AS rank
                           FROM chunk_fts JOIN chunks c ON c.id=chunk_fts.rowid
                           JOIN documents d ON d.id=c.document_id WHERE chunk_fts MATCH ?"""
                params: tuple[str, ...] = (match,)
                if kind:
                    sql += " AND d.kind = ?"
                    params += (kind,)
                rows = db.execute(sql + " ORDER BY rank LIMIT 50", params).fetchall()
                for row in rows:
                    previous = rows_by_chunk.get(row["chunk_id"])
                    if previous is None or row["rank"] < previous["rank"]:
                        rows_by_chunk[row["chunk_id"]] = row
        scored = []
        query_lower = query.casefold().strip()
        required = 1 if len(base_terms) == 1 else 2
        technical_terms = {term for term in base_terms if len(term) >= 5 and term.isascii() and term.isalnum()}
        chinese_evidence = set()
        for phrase in re.findall(r"[\u4e00-\u9fff]+", query_lower):
            length = min(5, max(2, math.ceil(len(phrase) / 2)))
            chinese_evidence.update(phrase[index:index + length] for index in range(len(phrase) - length + 1))
        for row in rows_by_chunk.values():
            if kind and row["kind"] != kind:
                continue
            tags = _row_tags(row)
            haystack = (row["title"] + " " + row["heading"] + " " + tags + " " + row["body"]).casefold()
            indexed = set(_words(haystack))
            overlap = len(indexed.intersection(searched_terms))
            direct_overlap = len(indexed.intersection(base_terms))
            alias_overlap = len(indexed.intersection(aliases))
            if direct_overlap < required and query_lower not in haystack and not (expand and alias_overlap >= 2):
                continue
            # A long Chinese phrase can qualify even when an ASCII hint is absent.
            if chinese_evidence and technical_terms and not indexed.intersection(technical_terms) and not any(
                phrase in haystack for phrase in chinese_evidence
            ):
                continue
            score = overlap * 2 + (8 if query_lower in haystack else 0)
            title_terms = set(_words(row["title"] + " " + row["heading"]))
            score += len(title_terms.intersection(searched_terms)) * 3
            if category and category.casefold() == row["category"].casefold():
                score += 2
            if row["kind"] == "navigation":
                score -= 5
            score += max(0.0, 2.0 - abs(float(row["rank"])) / 10.0)
            scored.append((score, row))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["rank"]))
        out: list[dict] = []
        per_doc: dict[str, int] = {}
        seen_hashes: set[str] = set()
        for _, row in scored:
            if row["chunk_hash"] in seen_hashes or per_doc.get(row["id"], 0) >= 2:
                continue
            seen_hashes.add(row["chunk_hash"])
            per_doc[row["id"]] = per_doc.get(row["id"], 0) + 1
            out.append({"document_id": row["id"], "title": row["title"], "heading": row["heading"],
                        "snippet": _snippet_near_match(row["body"], base_terms,
                                                       fallback_terms=expanded_terms),
                        "path": row["path"], "start_line": row["start_line"],
                        "end_line": row["end_line"], "kind": row["kind"], "category": row["category"],
                        "tags": _row_tags(row).split()[:20],
                        "author": row["author"], "original_url": row["original_url"], "license": row["license"],
                        "source": "Des-CTF-Knowledge", "snapshot_id": self.snapshot_id,
                        "source_url": SOURCE_URL.removesuffix(".git") + "/blob/" + self.snapshot_id.split("-v")[0] + "/" + quote(row["path"]) + "#L" + str(row["start_line"])})
            if len(out) >= limit:
                break
        if len(self._cache) > 256:
            self._cache.clear()
        self._cache[key] = out
        return out

    def read(self, document_id: str, *, start_line: int = 1, line_count: int = 120, char_offset: int = 0) -> dict:
        if not self.available:
            raise ValueError("External knowledge snapshot unavailable")
        start_line = max(1, int(start_line))
        line_count = min(max(1, int(line_count)), MAX_READ_LINES)
        char_offset = max(0, int(char_offset))
        with closing(_connect_readonly(self.snapshot / "index.sqlite3")) as db, db:
            doc = self._document(db, document_id)
            if not doc["text_available"]:
                raise ValueError("This document is binary; use stage_knowledge_script to copy it")
            path = self.snapshot / "source" / doc["path"]
            raw = path.read_bytes()
            if _digest(raw) != doc["sha256"]:
                raise ValueError("Knowledge snapshot file hash mismatch")
            lines = raw.decode("utf-8-sig").splitlines()
            selected: list[str] = []
            used = 0
            next_line = None
            next_char = 0
            for index in range(start_line - 1, min(len(lines), start_line - 1 + line_count)):
                remaining = MAX_READ_CHARS - used
                line = lines[index]
                offset = char_offset if index == start_line - 1 else 0
                prefix = f"{index + 1}: "
                part = line[offset:offset + max(0, remaining - len(prefix) - 1)]
                selected.append(prefix + part)
                used += len(prefix) + len(part) + 1
                if offset + len(part) < len(line):
                    next_line, next_char = index + 1, offset + len(part)
                    break
            if next_line is None and start_line - 1 + len(selected) < len(lines):
                next_line = start_line + len(selected)
            related = []
            if doc["kind"] in {"script", "tool"}:
                parent = str(PurePosixPath(doc["path"]).parent)
                for other in db.execute("SELECT id,path,kind FROM documents WHERE path LIKE ? ORDER BY path LIMIT 25",
                                        ((parent + "/%") if parent != "." else "",)):
                    if other["id"] != document_id and str(PurePosixPath(other["path"]).parent) == parent:
                        related.append({"document_id": other["id"], "path": other["path"], "kind": other["kind"]})
            return {"document_id": document_id, "path": doc["path"], "snapshot_id": self.snapshot_id,
                    "total_lines": len(lines), "text": "\n".join(selected), "next_start_line": next_line,
                    "next_char_offset": next_char, "author": doc["author"], "original_url": doc["original_url"],
                    "license": doc["license"], "tags": _row_tags(doc).split()[:20],
                    "related_files": related}

    async def stage(self, sandbox, document_id: str, extra_document_ids: list[str] | None = None) -> dict:
        import asyncio
        import shlex

        if not self.available:
            raise ValueError("External knowledge snapshot unavailable")
        ids = list(dict.fromkeys([document_id, *(extra_document_ids or [])]))
        if len(ids) > MAX_STAGE_FILES:
            raise ValueError("Too many files in one knowledge bundle")
        files = []
        total = 0
        with closing(_connect_readonly(self.snapshot / "index.sqlite3")) as db, db:
            for item_id in ids:
                doc = self._document(db, item_id)
                rel = PurePosixPath(doc["path"])
                if rel.is_absolute() or ".." in rel.parts:
                    raise ValueError("Unsafe knowledge path")
                host = self.snapshot / "source" / doc["path"]
                if host.is_symlink() or any(part.is_symlink() for part in host.parents if part != self.snapshot.parent):
                    raise ValueError("Knowledge symlink rejected")
                raw = await asyncio.to_thread(host.read_bytes)
                if _digest(raw) != doc["sha256"]:
                    raise ValueError("Knowledge snapshot file hash mismatch")
                total += len(raw)
                if total > MAX_STAGE_BYTES:
                    raise ValueError("Knowledge bundle exceeds 20 MiB")
                files.append((rel, raw, doc["sha256"], doc["kind"]))
        if files[0][3] != "script":
            raise ValueError("Primary document is not a script")
        bundle_id = _digest((self.snapshot_id + "/" + document_id).encode())[:16]
        target_root = PurePosixPath("/challenge/workspace/knowledge") / bundle_id
        staged = []
        conflicts = []
        for rel, raw, sha, _ in files:
            target = target_root / rel
            await sandbox.exec("mkdir -p " + shlex.quote(str(target.parent)), timeout_s=10)
            existence = await sandbox.exec("test -e " + shlex.quote(str(target)), timeout_s=10)
            existing = await sandbox.read_file_bytes(str(target)) if existence.exit_code == 0 else None
            if existing is not None:
                if _digest(existing) == sha:
                    staged.append({"path": str(target), "sha256": sha, "reused": True})
                    continue
                conflicts.append(str(target))
                continue
            await sandbox.write_file(str(target), raw)
            staged.append({"path": str(target), "sha256": sha, "reused": False})
        return {"bundle_dir": str(target_root), "files": staged, "conflicts": conflicts,
                "note": "Inspect the source and install any missing dependencies inside the sandbox before running it."}


def pin_snapshot(root: str | Path, run_id: str) -> str:
    """Persist the current snapshot for a run; resumed runs keep their original ID."""
    root = Path(root).resolve()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
        raise ValueError("Invalid run ID for knowledge snapshot")
    path = root / "runs" / (run_id + ".json")
    if path.exists():
        return str(json.loads(path.read_text(encoding="utf-8"))["snapshot_id"])
    snapshot_id = ExternalKnowledge(root).snapshot_id
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps({"snapshot_id": snapshot_id, "run_id": run_id, "created_at": time.time()}), encoding="utf-8")
    temp.replace(path)
    return snapshot_id
