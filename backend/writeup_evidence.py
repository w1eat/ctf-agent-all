"""Bounded, durable command evidence and media produced by real challenge runs.

Media is copied byte for byte. This module never synthesizes screenshots or
decides whether an image/audio artifact proves a flag.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import stat
import struct
import tempfile
import uuid
import zlib
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

logger = logging.getLogger(__name__)

MAX_ARTIFACTS = 12
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_ARTIFACT_TOTAL = 48 * 1024 * 1024
MAX_EVIDENCE_TEXT = 64_000
MAX_JOURNAL_BYTES = 8 * 1024 * 1024
MEDIA_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp", ".wav": "audio/wav",
    ".mp3": "audio/mpeg", ".txt": "text/plain", ".log": "text/plain",
    ".json": "application/json", ".jsonl": "application/x-ndjson",
    ".csv": "text/csv",
}
_active_call: ContextVar[Any] = ContextVar("writeup_evidence_call", default=None)


@contextmanager
def evidence_context(recorder: Any, tool: str, step: int):
    """Keep parallel executions attached to their own tool call."""
    token = _active_call.set((recorder, f"{tool}:{step}") if recorder else None)
    try:
        yield
    finally:
        _active_call.reset(token)


def observe_execution(result: Any) -> None:
    """Capture stdout/stderr and exit status before the tool's display limit."""
    active = _active_call.get()
    if active:
        recorder, key = active
        call = recorder.pending.get(key)
        if call is not None:
            call["execution"] = {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code}


def redact(value: Any, limit: int = 6000) -> str:
    """Apply the same credential redaction to prose, commands and outputs."""
    text = str(value or "").replace("\x00", "")[:limit]
    text = re.sub(r"(?i)\bBearer\s+[^\s'\"`]+", "Bearer [已脱敏]", text)
    text = re.sub(
        r"(?im)\b(Authorization|Cookie|Set-Cookie)\s*:\s*[^\r\n]+",
        lambda m: f"{m.group(1)}: [已脱敏]", text,
    )
    text = re.sub(
        r"(?i)\b([\w-]*(?:api[_-]?key|access[_-]?key|token|password|passwd|secret|username|account))"
        r"(\s*[=:]\s*['\"]?)([^\s,'\"}\]]+)",
        lambda m: f"{m.group(1)}{m.group(2)}[已脱敏]", text,
    )
    text = re.sub(r"(?i)\bsk-[A-Za-z0-9_-]{12,}\b", "[已脱敏密钥]", text)
    text = re.sub(r"\bAKIA[A-Z0-9]{16}\b", "[已脱敏密钥]", text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[已脱敏邮箱]", text)
    return re.sub(r"(?i)(https?://)[^\s/@:]+:[^\s/@]+@", r"\1[已脱敏账号]@", text)


def safe_path(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    """Reject traversal, absolute paths, symlinks and Windows junctions."""
    path = PurePosixPath(relative)
    if (not relative or "\\" in relative or "\x00" in relative or ":" in relative
            or path.is_absolute() or any(p in {"", ".", ".."} for p in relative.split("/"))):
        raise ValueError("Invalid evidence path")
    current = root
    for part in ("", *path.parts):
        current = current / part if part else current
        if current.is_symlink() or current.is_junction():
            raise ValueError("Links are not allowed in evidence paths")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence path escaped its root")
    if must_exist and not current.is_file():
        raise ValueError("Evidence file is missing")
    return current


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        Path(temporary).replace(path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _validate_media(content: bytes, suffix: str) -> None:
    signatures = {
        ".png": (b"\x89PNG\r\n\x1a\n",), ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",), ".gif": (b"GIF87a", b"GIF89a"),
        ".webp": (b"RIFF",), ".wav": (b"RIFF",),
    }
    if not content or len(content) > MAX_ARTIFACT_BYTES:
        raise ValueError("Empty or oversized artifact")
    if suffix in signatures and not content.startswith(signatures[suffix]):
        raise ValueError("Artifact extension does not match its file signature")
    if suffix in {".webp", ".wav"} and content[8:12] != (b"WEBP" if suffix == ".webp" else b"WAVE"):
        raise ValueError("Invalid RIFF artifact")
    if suffix == ".png" and (len(content) < 45 or content[12:16] != b"IHDR" or b"IEND" not in content[-12:]):
        raise ValueError("Incomplete PNG artifact")
    if suffix == ".png":
        position, saw_data, ended = 8, False, False
        while position + 12 <= len(content):
            size = struct.unpack_from(">I", content, position)[0]
            end = position + size + 12
            if end > len(content):
                raise ValueError("Truncated PNG chunk")
            kind = content[position + 4:position + 8]
            expected_crc = struct.unpack_from(">I", content, end - 4)[0]
            if zlib.crc32(content[position + 4:end - 4]) & 0xFFFFFFFF != expected_crc:
                raise ValueError("PNG chunk CRC mismatch")
            saw_data = saw_data or kind == b"IDAT"
            position = end
            if kind == b"IEND":
                ended = size == 0 and end == len(content)
                break
        if not saw_data or not ended:
            raise ValueError("Incomplete PNG data")
    if suffix in {".jpg", ".jpeg"} and not content.endswith(b"\xff\xd9"):
        raise ValueError("Incomplete JPEG artifact")
    if suffix == ".mp3" and not (content.startswith(b"ID3") or (len(content) > 1 and content[0] == 255 and content[1] & 224 == 224)):
        raise ValueError("Invalid MP3 artifact")


def store_artifact(
    challenge: Path, content: bytes, name: str, *, source: str, run_id: str = "",
    kind: str = "generated", caption: str = "", stage: str = "solver",
) -> dict[str, Any]:
    suffix = Path(name).suffix.lower()
    if suffix not in MEDIA_TYPES:
        raise ValueError("Unsupported evidence artifact type")
    _validate_media(content, suffix)
    if MEDIA_TYPES[suffix].startswith(("text/", "application/")):
        content = redact(content.decode("utf-8"), MAX_ARTIFACT_BYTES).encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    # A bounded filename keeps links usable; its directory is content addressed.
    clean_name = re.sub(r"[^\w.\-]", "_", Path(name).name, flags=re.UNICODE)[-100:]
    relative = f"solution/artifacts/{digest[:20]}/{clean_name}"
    target = safe_path(challenge, relative, must_exist=False)
    if target.exists() and target.read_bytes() != content:
        raise ValueError("Evidence artifact was modified")
    if not target.exists():
        atomic_write(target, content)
    return {
        "id": f"artifact-{digest[:16]}", "path": relative, "sha256": digest,
        "bytes": len(content), "media_type": MEDIA_TYPES[suffix], "kind": kind,
        "caption": redact(caption or Path(name).name, 500), "source": redact(source, 200),
        "run_id": run_id, "stage": stage, "created_at": datetime.now(UTC).isoformat(),
    }


def capture_artifact_files(
    challenge: str | Path, sandbox: Any, paths: tuple[str, ...] | list[str] = (), *,
    source: str, run_id: str = "", stage: str = "solver", discover: bool = False,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Copy registered outputs while the workspace is alive, before stop()."""
    workspace = str(getattr(sandbox, "workspace_dir", ""))
    if not workspace:
        return [], ["沙箱工作目录不可用，未保存证据产物。"] if paths else []
    root, destination = Path(workspace), Path(challenge).resolve()
    selected = list(dict.fromkeys(paths))
    if discover and root.is_dir():
        # Only replay-produced media are discovered automatically. Scripts and
        # arbitrary data files require explicit registration.
        for folder, directories, files in os.walk(root, followlinks=False):
            directories[:] = sorted(d for d in directories if not d.startswith(".") and not (
                (Path(folder) / d).is_symlink() or (Path(folder) / d).is_junction()))
            for name in sorted(files):
                if MEDIA_TYPES.get(Path(name).suffix.lower(), "").startswith(("image/", "audio/")):
                    selected.append((Path(folder) / name).relative_to(root).as_posix())
                    if len(selected) >= MAX_ARTIFACTS:
                        break
            if len(selected) >= MAX_ARTIFACTS:
                break
    saved, issues, total = [], [], 0
    for raw in list(dict.fromkeys(selected))[:MAX_ARTIFACTS]:
        try:
            relative = raw.removeprefix("/challenge/workspace/")
            path = safe_path(root, relative)
            info = path.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARTIFACT_BYTES or total + info.st_size > MAX_ARTIFACT_TOTAL:
                raise ValueError("Artifact size limit exceeded")
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                opened = os.fstat(descriptor)
                if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise ValueError("Artifact changed during capture")
                with os.fdopen(descriptor, "rb", closefd=False) as stream:
                    content = stream.read(MAX_ARTIFACT_BYTES + 1)
            finally:
                os.close(descriptor)
            if total + len(content) > MAX_ARTIFACT_TOTAL:
                raise ValueError("Artifact total size limit exceeded")
            artifact = store_artifact(destination, content, path.name, source=source, run_id=run_id, stage=stage)
            artifact["original_path"] = f"/challenge/workspace/{relative}"
            saved.append(artifact)
            total += len(content)
        except (OSError, ValueError, UnicodeError) as exc:
            issues.append(f"未保存产物 {redact(raw, 200)}：{redact(exc, 200)}")
    if len(selected) > MAX_ARTIFACTS:
        issues.append(f"产物超过 {MAX_ARTIFACTS} 个，已截断。")
    return saved, issues


def validated_artifacts(challenge: Path, artifacts: Any) -> list[dict[str, Any]]:
    checked, seen = [], set()
    for artifact in list(artifacts or ())[:MAX_ARTIFACTS * 3]:
        try:
            relative = str(artifact["path"])
            if not relative.startswith("solution/artifacts/"):
                continue
            path = safe_path(challenge, relative)
            if path.stat().st_size > MAX_ARTIFACT_BYTES:
                continue
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != artifact["sha256"]:
                continue
            suffix = path.suffix.lower()
            if suffix not in MEDIA_TYPES:
                continue
            _validate_media(content, suffix)
            identity = relative
            if identity in seen:
                continue
            seen.add(identity)
            checked.append({**artifact, "id": f"artifact-{artifact['sha256'][:16]}", "media_type": MEDIA_TYPES[suffix]})
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return checked


class EvidenceRecorder:
    """Write a separate journal before display/trace truncation, with call IDs."""

    def __init__(self, challenge: str | Path, source: str, run_id: str = "", *, provenance: str = "live") -> None:
        self.challenge = Path(challenge).resolve()
        self.token = uuid.uuid4().hex
        self.relative_path = f"solution/evidence/{self.token}/commands.jsonl"
        self.path = safe_path(self.challenge, self.relative_path, must_exist=False)
        self.source, self.run_id, self.provenance = source, run_id, provenance
        self.pending: dict[str, dict[str, Any]] = {}
        self._bytes = 0

    def call(self, tool: str, args: Any, step: int, call_id: str | None = None) -> None:
        if "knowledge" in tool or tool in {"check_findings", "notify_coordinator"}:
            return
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                args = {"input": args}
        if not isinstance(args, dict):
            return
        clean = {
            str(k): v if v is None or isinstance(v, (int, float, bool)) else redact(v, MAX_EVIDENCE_TEXT)
            for k, v in args.items() if k not in {"content", "data"}
        }
        self.pending[call_id or f"{tool}:{step}"] = {
            "tool": tool, "step": step, "arguments": clean,
            "command": clean.get("command", ""), "cwd": clean.get("cwd") or clean.get("workdir") or "/challenge",
        }

    def result(self, tool: str, output: Any, step: int, call_id: str | None = None) -> None:
        call = self.pending.pop(call_id or f"{tool}:{step}", None)
        if not call:
            return
        # Vision responses may contain a base64 image in the SDK representation.
        decoded = call.pop("execution", output)
        if isinstance(decoded, str):
            try:
                decoded = json.loads(decoded)
            except ValueError:
                pass
        exit_code = None
        if isinstance(decoded, dict) and ("stdout" in decoded or "stderr" in decoded):
            text = str(decoded.get("stdout") or "")
            if decoded.get("stderr"):
                text += "\n[stderr]\n" + str(decoded["stderr"])
            exit_code = decoded.get("exit_code", decoded.get("exitCode"))
        else:
            text = str(output or "")
        if tool.endswith("view_image"):
            text = "图像已返回；原图应通过 artifact_paths 归档。"
        row = {
            **call, "id": f"command-{self.token[:12]}-{call['step']}",
            "output": redact(text, MAX_EVIDENCE_TEXT), "output_chars": len(text),
            "truncated": len(text) > MAX_EVIDENCE_TEXT or "[truncated" in text or self.provenance == "historical_trace",
            "exit_code": exit_code,
            "source": self.source, "run_id": self.run_id, "provenance": self.provenance,
            "created_at": datetime.now(UTC).isoformat(),
        }
        data = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
        if self._bytes + len(data) > MAX_JOURNAL_BYTES:
            return
        try:
            safe_path(self.challenge, self.relative_path, must_exist=False)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as stream:
                stream.write(data)
                stream.flush()
            self._bytes += len(data)
        except (OSError, ValueError):
            logger.warning("Could not persist writeup command evidence", exc_info=True)


def load_command_evidence(challenge: Path, paths: Any, *, run_id: str = "", limit: int = 24) -> list[dict[str, Any]]:
    rows = []
    for relative in list(dict.fromkeys(paths or ()))[:6]:
        try:
            if not str(relative).startswith("solution/evidence/"):
                continue
            path = safe_path(challenge, relative)
            if path.stat().st_size > MAX_JOURNAL_BYTES:
                continue
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(row, dict) or not row.get("id") or (run_id and row.get("run_id") != run_id):
                        continue
                    row["journal_path"] = relative
                    rows.append(row)
        except (OSError, ValueError):
            continue
    if len(rows) > limit:
        # Preserve the start, middle and end instead of only the final messages.
        indices = sorted({round(i * (len(rows) - 1) / (limit - 1)) for i in range(limit)})
        rows = [rows[i] for i in indices]
    return rows
