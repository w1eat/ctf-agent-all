"""Durable, evidence-backed Chinese CTF writeups.

The solver's temporary workspace is deleted on stop.  EXP files therefore have
to be captured while its sandbox is alive; a writeup never reconstructs files
from a (possibly truncated) model trace.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import shlex
import stat
import tempfile
import uuid
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

from backend.cost_tracker import CostTracker
from backend.sandbox import DockerSandbox
from backend.writeup_evidence import (
    MAX_EVIDENCE_TEXT,
    MAX_JOURNAL_BYTES,
    atomic_write,
    capture_artifact_files,
    load_command_evidence,
    redact,
    safe_path,
    validated_artifacts,
)

logger = logging.getLogger(__name__)

MAX_EXP_FILES = 12
MAX_EXP_FILE_BYTES = 256 * 1024
MAX_EXP_TOTAL_BYTES = 1024 * 1024
MAX_CONTEXT_TEXT = 6000
CONFIRMATION_SOURCES = {"platform_confirmed", "independent_quorum", "candidate_found"}
SOURCE_PRIORITY = {"candidate_found": 0, "independent_quorum": 1, "platform_confirmed": 2}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".js", ".rb", ".pl", ".php"}


def _digest(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        Path(temporary).replace(path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"version": 1, "current_key": "", "status": "", "records": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError(f"Invalid writeup manifest: {path}")
    return data


def _value(obj: Any, key: str, default: Any = None) -> Any:
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def _short(value: Any, limit: int = MAX_CONTEXT_TEXT) -> str:
    return str(value or "").replace("\x00", "")[:limit]


def _redact(value: Any, limit: int = MAX_CONTEXT_TEXT) -> str:
    """Remove common credentials before persisting text or publishing an EXP."""
    return redact(value, limit)


def _source_component(source: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", source).strip(".-")[:48] or "solver"
    return f"{name}-{_digest(source)[:8]}"


def _safe_run_command(command: Any, flag: str) -> str:
    if not command:
        return ""
    value = str(command).strip()
    if len(value) > 2000 or flag in value or _redact(value, len(value) + 1) != value:
        return "[unsupported]"
    if re.search(r"[;&|<>$`\r\n]", value):
        return "[unsupported]"
    try:
        tokens = shlex.split(value)
    except ValueError:
        return "[unsupported]"
    if len(tokens) < 2 or tokens[0] not in {"python", "python3", "bash", "sh", "node", "ruby", "perl", "php"}:
        return "[unsupported]"
    try:
        _workspace_parts(tokens[1])
    except ValueError:
        return "[unsupported]"
    return value


def _is_safe_file_below(root: Path, path: Path) -> bool:
    try:
        if root.is_symlink() or not path.is_relative_to(root):
            return False
        current = root
        for part in path.relative_to(root).parts:
            current = current / part
            if current.is_symlink():
                return False
        return path.is_file()
    except OSError:
        return False


def _workspace_parts(path: str) -> tuple[str, ...]:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        raise ValueError("EXP path must use POSIX syntax inside /challenge/workspace")
    prefix = "/challenge/workspace/"
    relative = path[len(prefix):] if path.startswith(prefix) else path
    if path.startswith("/") and not path.startswith(prefix):
        raise ValueError("EXP path is outside /challenge/workspace")
    parts = tuple(relative.split("/"))
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("EXP path contains an empty or traversal component")
    if any(":" in part for part in parts):
        raise ValueError("EXP path contains an invalid component")
    return parts


def capture_exp_files(
    challenge_dir: str | Path,
    sandbox: Any,
    exp_paths: Iterable[str],
    flag: str,
    source: str,
) -> tuple[str, ...]:
    """Copy only named regular files out of a live solver workspace.

    Paths can be relative to /challenge/workspace or absolute container paths
    beginning with that directory.  Symlinks in any component are forbidden.
    Content-addressed draft paths prevent a later attempt from silently changing
    a previously captured script.
    """
    workspace_dir = str(getattr(sandbox, "workspace_dir", ""))
    root = Path(workspace_dir)
    if not workspace_dir or not root.is_dir() or root.is_symlink() or not flag:
        raise ValueError("A live sandbox workspace and flag are required")
    challenge = Path(challenge_dir).resolve()
    draft_root = challenge / ".writeup-drafts" / _digest(flag)[:20] / _source_component(source)
    captured: list[str] = []
    total = 0
    for raw in dict.fromkeys(exp_paths or ()):
        if len(captured) >= MAX_EXP_FILES:
            raise ValueError(f"At most {MAX_EXP_FILES} EXP files may be exported")
        parts = _workspace_parts(raw)
        current = root
        for part in parts:
            current = current / part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f"Symlink is not allowed in EXP path: {raw}")
        info = current.stat(follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"EXP is not a regular file: {raw}")
        if info.st_size > MAX_EXP_FILE_BYTES or total + info.st_size > MAX_EXP_TOTAL_BYTES:
            raise ValueError(f"EXP exceeds size limit: {raw}")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(current, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError(f"EXP changed during capture: {raw}")
            with os.fdopen(descriptor, "rb", closefd=False) as handle:
                content = handle.read(MAX_EXP_FILE_BYTES + 1)
        finally:
            os.close(descriptor)
        if len(content) > MAX_EXP_FILE_BYTES or total + len(content) > MAX_EXP_TOTAL_BYTES:
            raise ValueError(f"EXP exceeds size limit: {raw}")
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"EXP must be a UTF-8 text file: {raw}") from exc
        if flag in decoded:
            raise ValueError(f"EXP directly contains the confirmed flag: {raw}")
        if _redact(decoded, len(decoded) + 1) != decoded:
            raise ValueError(f"EXP contains credentials and cannot be retained: {raw}")
        total += len(content)
        target = draft_root / _digest(content)[:16] / Path(*parts)
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f"Captured EXP changed unexpectedly: {target}")
        if not target.exists():
            _atomic_bytes(target, content)
        captured.append(target.relative_to(challenge).as_posix())
    return tuple(captured)


def _challenge_payload(meta: Any) -> dict[str, Any]:
    if is_dataclass(meta):
        data = asdict(meta)
    elif isinstance(meta, dict):
        data = meta
    else:
        data = {key: getattr(meta, key, None) for key in ("name", "category", "description", "connection_info", "value", "tags", "hints")}
    return {
        "name": _redact(data.get("name", "Unknown"), 200),
        "category": _redact(data.get("category", ""), 100),
        "description": _redact(data.get("description", ""), 4000),
        "connection_info": _redact(data.get("connection_info", ""), 500),
        "value": data.get("value", 0),
        "tags": [_redact(tag, 100) for tag in (data.get("tags") or [])[:20]],
        "hints": [_redact(hint, 500) for hint in (data.get("hints") or [])[:10]],
    }


def _saved_exp_paths(result: Any, challenge: Path, flag: str, *, preferred: Iterable[str] = ()) -> list[str]:
    supplied = (
        _value(result, "saved_exp_paths", None)
        or _value(result, "exp_files", None)
        or _value(result, "exp_paths", None)
        or preferred
        or ()
    )
    prefix = PurePosixPath(".writeup-drafts") / _digest(flag)[:20]
    selected: list[str] = []
    for raw in supplied:
        try:
            path = PurePosixPath(str(raw))
            if path.is_absolute() or ".." in path.parts or path.parts[:2] != prefix.parts:
                continue
            local = challenge.joinpath(*path.parts)
            if _is_safe_file_below(challenge / ".writeup-drafts", local) and local.stat().st_size <= MAX_EXP_FILE_BYTES:
                selected.append(path.as_posix())
        except (OSError, ValueError):
            continue
    if not selected:
        # A distinct verifier may win after the proposer already exited.  Its
        # result can then lack the proposer's paths even though those files were
        # explicitly captured before that sandbox stopped.
        drafts = challenge / ".writeup-drafts" / _digest(flag)[:20]
        if drafts.is_dir() and not drafts.is_symlink():
            for local in sorted(drafts.rglob("*")):
                try:
                    if _is_safe_file_below(drafts, local) and local.stat().st_size <= MAX_EXP_FILE_BYTES:
                        selected.append(local.relative_to(challenge).as_posix())
                except OSError:
                    continue
                if len(selected) >= MAX_EXP_FILES:
                    break
    return list(dict.fromkeys(selected))[:MAX_EXP_FILES]


def _record_key(flag: str, confirmation_source: str) -> str:
    return f"{_digest(flag)[:20]}:{confirmation_source}"


def _file_matches_known_hash(path: Path, manifest: dict[str, Any]) -> bool:
    if not path.exists():
        return True
    actual = _digest(path.read_bytes())
    hashes = {
        record.get(field)
        for record in manifest.get("records", [])
        for field in ("writeup_sha256", "planned_sha256")
    }
    return actual in hashes


def _input_files(challenge: Path) -> list[dict[str, Any]]:
    files = []
    root = challenge / "distfiles"
    if not root.is_dir() or root.is_symlink() or root.is_junction():
        return files
    for path in sorted(root.rglob("*")):
        try:
            safe_path(challenge, path.relative_to(challenge).as_posix())
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            files.append({"path": path.relative_to(challenge).as_posix(), "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
        except (OSError, ValueError):
            continue
        if len(files) >= 50:
            break
    return files


def _journal_hashes(challenge: Path, paths: Iterable[str]) -> dict[str, str]:
    hashes = {}
    for relative in paths:
        try:
            if not relative.startswith("solution/evidence/"):
                continue
            path = safe_path(challenge, relative)
            if path.stat().st_size <= MAX_JOURNAL_BYTES:
                hashes[relative] = _digest(path.read_bytes())
        except (OSError, ValueError):
            continue
    return hashes


def _excerpt(value: Any, limit: int = 3500) -> str:
    text = _redact(value, MAX_EVIDENCE_TEXT)
    if len(text) <= limit:
        return text
    return text[:limit * 2 // 3] + "\n…［中间输出省略，见完整证据记录］…\n" + text[-limit // 3:]


def _code_block(value: Any, language: str = "text", limit: int = 8000) -> list[str]:
    text = _excerpt(value, limit)
    longest = max((len(match.group()) for match in re.finditer(r"~+", text)), default=0)
    fence = "~" * max(3, longest + 1)
    return [f"{fence}{language}", text, fence, ""]


def _link(path: str) -> str:
    return quote(path, safe="/._-")


def _heading_ref(title: str) -> str:
    text = re.sub(r"[^\w\s-]", "", title.lower()).strip()
    return "#" + re.sub(r"\s+", "-", text)


def _table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", " ")


def _callout(label: str, value: Any, limit: int = 2000) -> list[str]:
    text = _redact(value, limit)
    return [f"> **{label}**", ">", *(f"> {line}" if line else ">" for line in text.splitlines()), ""]


def _artifact_lines(artifact: dict[str, Any], title: str) -> list[str]:
    caption = _redact(artifact.get("caption") or "证据产物", 500).replace("[", "（").replace("]", "）").replace("\n", " ")
    kind = {"screenshot": "真实页面截图", "historical_record": "历史记录"}.get(artifact.get("kind"), "运行生成的产物")
    stage = {"solver": "求解阶段", "replay": "复现阶段", "submission": "提交阶段"}.get(artifact.get("stage"), "已归档")
    path = _link(artifact["path"])
    lines = [f"#### {title}", ""]
    if artifact["media_type"].startswith("image/"):
        lines += [f"![{caption}]({path})", "", f"*{caption}*", ""]
    else:
        lines += [f"**{caption}** · [打开文件]({path})", ""]
    lines += [f"{stage} · {kind} · [原文件]({path}) · [校验信息](#文件校验清单)", ""]
    return lines


def _command_lines(row: dict[str, Any], number: int, *, appendix: bool = False) -> list[str]:
    heading = f"命令记录 {number:02d}" if appendix else f"执行命令 {number:02d}"
    lines = [f"#### {heading}", ""]
    if row.get("command"):
        language = "powershell" if re.match(r"^[A-Za-z]:", row.get("cwd", "")) else "bash"
        lines += _code_block(row["command"], language, 12000)
    else:
        lines += ["**操作参数**", "", *_code_block(json.dumps(row.get("arguments", {}), ensure_ascii=False, indent=2), "json", 3000)]
    if row.get("truncated"):
        lines += _callout("记录限制", "该记录存在截断；未保留的内容无法据此还原。")
    if row.get("provenance") == "historical_trace":
        lines += _callout("历史证据", "来源为历史工具日志，未在本次重新执行。")
    output = str(row.get("output") or "（无输出记录）")
    exit_label = f" · 退出码 {row['exit_code']}" if row.get("exit_code") is not None else ""
    metadata = [
        f"- 证据编号：`{row['id']}`",
        f"- 工具：`{row.get('tool', '')}`",
        f"- 起始目录：`{row.get('cwd', '/challenge')}`",
        f"- [查看已保留的完整证据记录]({_link(row['journal_path'])})", "",
    ]
    if appendix or (len(output) <= 1200 and len(output.splitlines()) <= 14):
        lines += ["**实际输出**", "", *_code_block(output)]
    if appendix:
        if row.get("exit_code") is not None:
            lines += [f"退出码：`{row['exit_code']}`", ""]
        lines += metadata
    else:
        lines += [f"[查看实际输出与执行记录]({_heading_ref(f'命令记录 {number:02d}')}){exit_label}", ""]
    return lines


def _exp_source_lines(challenge: Path, files: list[Path]) -> list[str]:
    languages = {".py": "python", ".sh": "bash", ".js": "javascript", ".ts": "typescript",
                 ".c": "c", ".h": "c", ".cpp": "cpp", ".go": "go", ".rs": "rust",
                 ".rb": "ruby", ".pl": "perl", ".php": "php"}
    lines = []
    for index, path in enumerate(files[:MAX_EXP_FILES], 1):
        try:
            relative = path.relative_to(challenge).as_posix()
            safe_path(challenge, relative)
            if path.stat().st_size > MAX_EXP_FILE_BYTES:
                continue
            content = path.read_text(encoding="utf-8")
        except (OSError, ValueError, UnicodeError):
            continue
        body = [f"### EXP 源码 {index:02d}", "", f"**文件**：[{relative}]({_link(relative)})", ""]
        if len(content) > 16_000:
            body += ["以下展示前 16000 个字符，完整内容见源码文件。", ""]
        body += _code_block(content[:16_000], languages.get(path.suffix.lower(), "text"), 16_000)
        lines += body
    return lines


class WriteupManager:
    """Persists flag candidates and confirmations before launching writeup jobs."""

    def __init__(self, settings: Any, default_model_spec: str = "", cost_tracker: CostTracker | None = None) -> None:
        self.settings = settings
        self.default_model_spec = default_model_spec
        self.cost_tracker = cost_tracker if cost_tracker is not None else CostTracker()
        self._tasks: dict[Path, asyncio.Task[None]] = {}

    async def record_and_schedule(
        self,
        challenge_dir: str | Path,
        meta: Any,
        flag: str,
        confirmation_source: str,
        solver_result: Any = None,
        model_spec: str = "",
        evidence: Iterable[str] = (),
        force: bool = False,
    ) -> Path | None:
        """Record a flag candidate or confirmation and schedule writing immediately.

        Candidates are explicitly labelled unverified. A later independent or
        platform confirmation upgrades the writeup without discarding evidence.
        """
        if confirmation_source not in CONFIRMATION_SOURCES:
            raise ValueError(f"Unknown confirmation source: {confirmation_source}")
        if not flag or flag != flag.strip():
            return None
        if solver_result is not None and _value(solver_result, "flag") != flag:
            logger.warning("Writeup skipped: solver result does not match recorded flag")
            return None
        if confirmation_source == "independent_quorum":
            verified_by = set(_value(solver_result, "verified_by", ()) or ())
            quorum = max(2, int(getattr(self.settings, "flag_verification_quorum", 2) or 2))
            if _value(solver_result, "status") != "verified" or len(verified_by) < quorum:
                logger.warning("Writeup skipped: independent verifier quorum was not reached")
                return None

        challenge = Path(challenge_dir).resolve()
        manifest_path = challenge / "solution" / "manifest.json"
        writeup_path = challenge / "writeup.md"
        manifest = _read_manifest(manifest_path)
        key = _record_key(flag, confirmation_source)
        existing = next((item for item in manifest["records"] if item.get("key") == key), None)
        # Keep stronger confirmations and never replace an accepted solution
        # with a late unverified candidate, even for a different flag.
        stronger = next(
            (item for item in manifest["records"]
             if SOURCE_PRIORITY.get(item.get("confirmation_source"), -1)
             > SOURCE_PRIORITY[confirmation_source]
             and (item.get("flag") == flag or confirmation_source == "candidate_found")),
            None,
        )
        if stronger:
            return writeup_path if writeup_path.exists() else None
        previous = existing or next((item for item in manifest["records"] if item.get("flag") == flag), None)
        manual_edit = writeup_path.exists() and not force and not _file_matches_known_hash(writeup_path, manifest)
        incoming_logs = tuple(_value(solver_result, "evidence_logs", ()) or ())
        incoming_assets = _value(solver_result, "saved_artifacts", ()) or ()
        material_changed = bool(existing and (
            set(incoming_logs) - set(existing.get("evidence_logs", ()))
            or {item.get("sha256") for item in incoming_assets} - {item.get("sha256") for item in existing.get("saved_artifacts", ())}
            or any(existing.get("evidence_log_sha256", {}).get(path) != digest
                   for path, digest in _journal_hashes(challenge, incoming_logs).items())
        ))
        if (existing and existing.get("status") in {"complete", "needs_review"}
                and existing.get("format_version", 1) >= 2
                and not material_changed and not force and writeup_path.exists() and not manual_edit):
            return writeup_path

        result_evidence = _value(solver_result, "evidence", ()) or ()
        combined_evidence = list(result_evidence) + list(evidence or ())
        if not combined_evidence and previous:
            combined_evidence = list(previous.get("evidence") or ())
        steps = _value(solver_result, "solution_steps", ()) or (previous.get("solution_steps", ()) if previous else ())
        if isinstance(steps, str):
            steps = (steps,)
        selected_model = (
            getattr(self.settings, "writeup_model_spec", "")
            or model_spec
            or (previous.get("model_spec", "") if previous else "")
            or self.default_model_spec
        )
        record = {
            "key": key,
            "flag": flag,
            "confirmation_source": confirmation_source,
            "model_spec": selected_model,
            "run_id": str(getattr(self.settings, "challenge_run_id", "") or ""),
            "verified_by": sorted(set(_value(solver_result, "verified_by", ()) or ())) or (list(previous.get("verified_by", ())) if previous else []),
            "challenge": _challenge_payload(meta),
            "findings_summary": _redact(_value(solver_result, "findings_summary", "") or (previous.get("findings_summary", "") if previous else ""), 2000),
            "solution_steps": [_redact(step, 1000) for step in list(steps)[:20]],
            "evidence": [_redact(item, 1000) for item in combined_evidence[:20]],
            "saved_exp_paths": _saved_exp_paths(solver_result, challenge, flag, preferred=previous.get("saved_exp_paths", ()) if previous else ()),
            "exp_run_command": _safe_run_command(_value(solver_result, "exp_run_command", "") or (previous.get("exp_run_command", "") if previous else ""), flag),
            "saved_artifacts": validated_artifacts(challenge, [
                *(previous.get("saved_artifacts", ()) if previous else ()),
                *(_value(solver_result, "saved_artifacts", ()) or ()),
            ]),
            "artifact_issues": [_redact(item, 500) for item in (_value(solver_result, "artifact_issues", ()) or ())],
            "evidence_logs": list(dict.fromkeys([
                *(_value(solver_result, "evidence_logs", ()) or ()),
                *(previous.get("evidence_logs", ()) if previous else ()),
            ]))[:6],
            "sandbox_image": str(getattr(self.settings, "sandbox_image", "ctf-sandbox")),
            "format_version": 2,
            "generation_id": uuid.uuid4().hex,
            "exp_sha256": dict(existing.get("exp_sha256", {})) if existing else {},
            "status": "needs_review" if manual_edit else "pending",
            "replay": {},
            "writeup_sha256": existing.get("writeup_sha256") if existing else None,
            "planned_sha256": existing.get("planned_sha256") if existing else None,
            "created_at": previous.get("created_at", _now()) if previous else _now(),
            "updated_at": _now(),
        }
        if existing:
            manifest["records"][manifest["records"].index(existing)] = record
        else:
            manifest["records"].append(record)
        manifest["current_key"] = key
        manifest["status"] = record["status"]
        if manual_edit:
            record["error"] = "检测到人工修改的 writeup.md，已保留原文件。"
        _atomic_json(manifest_path, manifest)
        if confirmation_source in {"platform_confirmed", "independent_quorum"} and solver_result is not None:
            try:
                from backend.local_knowledge import write_verified_draft

                write_verified_draft(meta, solver_result, confirmation_source,
                                     run_id=str(getattr(self.settings, "challenge_run_id", "") or ""))
            except (OSError, ValueError):
                logger.exception("Could not create reviewed knowledge draft for %s", challenge)
        if not manual_edit:
            self._schedule(challenge, force=force)
        return writeup_path

    def _schedule(self, challenge: Path, *, force: bool = False) -> None:
        existing = self._tasks.get(challenge)
        if existing and not existing.done():
            return
        task = asyncio.create_task(self._drain(challenge, force=force), name=f"writeup-{challenge.name}")
        self._tasks[challenge] = task
        task.add_done_callback(lambda finished: self._tasks.pop(challenge, None) if self._tasks.get(challenge) is finished else None)

    async def _drain(self, challenge: Path, *, force: bool) -> None:
        manifest_path = challenge / "solution" / "manifest.json"
        processed: set[tuple[str, str]] = set()
        while True:
            manifest = _read_manifest(manifest_path)
            key = manifest.get("current_key", "")
            record = next((item for item in manifest["records"] if item.get("key") == key), None)
            revision = (key, record.get("generation_id", "")) if record else (key, "")
            if not record or revision in processed or record.get("status") not in {"pending", "failed"}:
                return
            processed.add(revision)
            try:
                await self._generate(challenge, record, force=force)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Writeup generation failed for %s: %s", challenge, exc, exc_info=True)
                latest = _read_manifest(manifest_path)
                matching = next((item for item in latest["records"] if item.get("key") == key), None)
                if matching and matching.get("generation_id", "") == record.get("generation_id", ""):
                    matching["status"] = "failed"
                    matching["error"] = _redact(exc, 500)
                    matching["updated_at"] = _now()
                    if latest.get("current_key") == key:
                        latest["status"] = "failed"
                    _atomic_json(manifest_path, latest)

    async def _generate(self, challenge: Path, record: dict[str, Any], *, force: bool) -> None:
        from backend.model_usage import usage_accounting
        from backend.writeup_writer import write_solution_sections

        manifest_path = challenge / "solution" / "manifest.json"
        exp_files, exp_issue = self._publish_exp(challenge, record, force=force)
        if record["confirmation_source"] == "candidate_found":
            # Writing a candidate must not wait for a fresh sandbox or treat
            # replay as a prerequisite for publishing the writeup.
            replay = {
                "status": "manual",
                "reason": "候选 Flag 尚未进行平台验证或自动复现；此题解依据求解器记录生成。",
                "command": "", "exit_code": None, "stdout": "", "stderr": "",
            }
            if exp_issue:
                replay["reason"] += f" EXP 待检查：{exp_issue}"
        else:
            replay = await self._replay(challenge, record["flag"], exp_files, exp_issue, record.get("exp_run_command", ""))
        commands = load_command_evidence(challenge, record.get("evidence_logs", ()), run_id=record.get("run_id", ""))
        supplied_artifacts = [*record.get("saved_artifacts", ()), *replay.get("artifacts", ())]
        # Submission evidence is bound to this exact flag and competition run.
        submission_path = challenge / "solution" / "submissions" / f"{_digest(record['flag'])[:20]}.json"
        try:
            safe_path(challenge, submission_path.relative_to(challenge).as_posix())
            submission = json.loads(submission_path.read_text(encoding="utf-8"))
            if submission.get("flag_sha256") == _digest(record["flag"]) and submission.get("run_id") == record.get("run_id", ""):
                supplied_artifacts += submission.get("artifacts", [])
        except (OSError, ValueError, TypeError):
            pass
        artifacts = validated_artifacts(challenge, supplied_artifacts)
        inputs = _input_files(challenge)
        issues = [*record.get("artifact_issues", ()), *replay.get("artifact_issues", ())]
        if len({item.get("path") for item in supplied_artifacts}) > len(artifacts):
            issues.append("部分证据产物缺失、被修改或格式无效，未嵌入题解。")
        record = {**record, "saved_artifacts": artifacts, "inputs": inputs, "artifact_issues": issues}
        context_exp_files, remaining = [], 48_000
        for path in exp_files:
            content = path.read_text(encoding="utf-8", errors="replace")
            selected = _redact(content, min(16_000, remaining))
            context_exp_files.append({"path": path.relative_to(challenge).as_posix(), "content": selected,
                                      "content_truncated": len(content) > len(selected)})
            remaining -= len(selected)
        command_context, remaining = [], 72_000
        for row in commands:
            entry = {**row, "command": _excerpt(row.get("command", ""), 4000),
                     "output": _excerpt(row.get("output", ""), 2500),
                     "arguments": _excerpt(json.dumps(row.get("arguments", {}), ensure_ascii=False), 2000)}
            length = len(json.dumps(entry, ensure_ascii=False))
            if length > remaining:
                continue
            command_context.append(entry)
            remaining -= length
        context = {
            "challenge": record["challenge"],
            "confirmation_source": record["confirmation_source"],
            "flag": record["flag"],
            "findings_summary": record["findings_summary"],
            "solution_steps": record["solution_steps"],
            "evidence": record["evidence"],
            "exp_files": context_exp_files,
            "replay": replay,
            "environment": {"sandbox_image": record.get("sandbox_image", ""), "working_directory": "/challenge", "workspace": "/challenge/workspace", "inputs": inputs},
            "command_evidence": command_context,
            "artifacts": artifacts,
            "artifact_issues": issues,
        }
        has_method = bool(record["findings_summary"] or record["solution_steps"] or record["saved_exp_paths"] or commands)
        if has_method:
            timeout = max(1, int(getattr(self.settings, "writeup_timeout_seconds", 180) or 180))
            logger.info("Generating writeup for %s with %s", challenge, record["model_spec"])
            with usage_accounting(self.cost_tracker, f"writeup:{challenge}/{record['model_spec']}"):
                sections = await asyncio.wait_for(
                    write_solution_sections(self.settings, record["model_spec"], context), timeout=timeout
                )
        else:
            sections = {
                "principle": "已有 Flag 记录，但缺少可审计的解题过程。",
                "steps": ["缺少可复现的解题步骤，待补充。"],
                "exp_usage": "没有保存 EXP，请人工补充。",
                "limitations": "只有 Flag 记录，不能据此还原解法或证明平台接受。",
            }
        markdown = self._render(record, sections, replay, exp_files, challenge, commands=commands)
        digest = _digest(markdown)
        latest = _read_manifest(manifest_path)
        key = record["key"]
        if latest.get("current_key") != key:
            return
        target = next(item for item in latest["records"] if item.get("key") == key)
        if target.get("generation_id", "") != record.get("generation_id", ""):
            return
        writeup = challenge / "writeup.md"
        if writeup.exists() and not force and not _file_matches_known_hash(writeup, latest):
            target["status"] = latest["status"] = "needs_review"
            target["error"] = "检测到人工修改的 writeup.md，已保留原文件。"
            _atomic_json(manifest_path, latest)
            return
        target["planned_sha256"] = digest
        target["replay"] = replay
        target["saved_artifacts"] = artifacts
        target["inputs"] = inputs
        target["artifact_issues"] = issues
        target["evidence_log_sha256"] = _journal_hashes(challenge, record.get("evidence_logs", ()))
        _atomic_json(manifest_path, latest)
        _atomic_bytes(writeup, markdown.encode("utf-8"))
        target["status"] = latest["status"] = (
            "needs_review" if replay["status"] in {"needs_review", "artifacts_generated"} or not has_method or issues else "complete"
        )
        target["writeup_sha256"] = digest
        target["planned_sha256"] = None
        target["updated_at"] = _now()
        _atomic_json(manifest_path, latest)

    def _publish_exp(self, challenge: Path, record: dict[str, Any], *, force: bool) -> tuple[list[Path], str]:
        manifest = _read_manifest(challenge / "solution" / "manifest.json")
        known = {
            name: digest
            for item in manifest["records"]
            for name, digest in (item.get("exp_sha256") or {}).items()
        }
        copied: list[Path] = []
        issues: list[str] = []
        hashes: dict[str, str] = {}
        for raw in record.get("saved_exp_paths", []):
            path = PurePosixPath(raw)
            parts = path.parts
            if len(parts) < 5 or parts[0] != ".writeup-drafts" or parts[1] != _digest(record["flag"])[:20] or ".." in parts:
                issues.append("EXP 草稿路径无效")
                continue
            source = challenge.joinpath(*parts)
            if not _is_safe_file_below(challenge / ".writeup-drafts", source) or source.stat().st_size > MAX_EXP_FILE_BYTES:
                issues.append(f"EXP 草稿缺失或无效：{raw}")
                continue
            try:
                content = source.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                issues.append(f"EXP 不是 UTF-8 文本：{raw}")
                continue
            if record["flag"] in content:
                issues.append(f"EXP 直接包含完整 Flag，未发布：{raw}")
                continue
            safe_content = _redact(content, MAX_EXP_FILE_BYTES + 1)
            if safe_content != content:
                issues.append(f"EXP 含凭据信息，已脱敏：{raw}")
            relative = Path(*parts[4:])
            target = challenge / "exp" / relative
            if target.parent.is_symlink() or (challenge / "exp").is_symlink():
                issues.append("EXP 目录包含符号链接，已拒绝发布")
                continue
            if target.exists() and not force and known.get(target.relative_to(challenge).as_posix()) != _digest(target.read_bytes()):
                issues.append(f"EXP 已有人工作出修改，保留原文件：{target.name}")
                continue
            _atomic_bytes(target, safe_content.encode("utf-8"))
            copied.append(target)
            hashes[target.relative_to(challenge).as_posix()] = _digest(target.read_bytes())
        latest = _read_manifest(challenge / "solution" / "manifest.json")
        for item in latest["records"]:
            if item.get("key") == record["key"]:
                item["exp_sha256"] = hashes
                break
        _atomic_json(challenge / "solution" / "manifest.json", latest)
        return copied, "；".join(issues)

    async def _replay(self, challenge: Path, flag: str, files: list[Path], issue: str, run_command: str) -> dict[str, Any]:
        if issue:
            return {"status": "needs_review", "reason": issue, "command": "", "exit_code": None, "stdout": "", "stderr": ""}
        executable = next((path for path in files if path.suffix.lower() in EXECUTABLE_SUFFIXES), None)
        if executable is None:
            return {"status": "manual", "reason": "没有可自动运行的 EXP；请按题解步骤人工复现。", "command": "", "exit_code": None, "stdout": "", "stderr": ""}
        if run_command == "[unsupported]":
            return {"status": "manual", "reason": "提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。", "command": "", "exit_code": None, "stdout": "", "stderr": ""}
        if run_command:
            tokens = shlex.split(run_command)
            script_relative = Path(*_workspace_parts(tokens[1]))
            candidate = challenge / "exp" / script_relative
            if candidate not in files:
                return {"status": "manual", "reason": "运行命令引用的脚本不在已保存的 EXP 中，需人工复现。", "command": "", "exit_code": None, "stdout": "", "stderr": ""}
            interpreter = tokens[0]
            executable = candidate
            args = tokens[2:]
        else:
            interpreter = {".py": "python3", ".sh": "bash", ".js": "node", ".rb": "ruby", ".pl": "perl", ".php": "php"}[executable.suffix.lower()]
            args = []
        relative = executable.relative_to(challenge / "exp").as_posix()
        command = "cd /challenge/workspace && " + " ".join(
            shlex.quote(item) for item in (interpreter, relative, *args)
        )
        sandbox = DockerSandbox(
            image=getattr(self.settings, "sandbox_image", "ctf-sandbox"),
            challenge_dir=str(challenge),
            memory_limit=getattr(self.settings, "container_memory_limit", "16g"),
        )
        timeout = max(1, int(getattr(self.settings, "writeup_replay_timeout_seconds", 120) or 120))
        try:
            await asyncio.wait_for(sandbox.start(), timeout=45)
            workspace = Path(sandbox.workspace_dir)
            for path in files:
                destination = workspace / path.relative_to(challenge / "exp")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(path.read_bytes())
            result = await asyncio.wait_for(sandbox.exec(command, timeout_s=timeout), timeout=timeout + 35)
            output = (result.stdout or "") + "\n" + (result.stderr or "")
            exact = bool(re.search(rf"(?<![A-Za-z0-9_]){re.escape(flag)}(?![A-Za-z0-9_])", output))
            artifacts, artifact_issues = capture_artifact_files(
                challenge, sandbox, source="EXP replay",
                run_id=str(getattr(self.settings, "challenge_run_id", "") or ""),
                stage="replay", discover=True,
            )
            status = "needs_review"
            if result.exit_code == 0 and exact:
                status = "verified"
            elif result.exit_code == 0 and artifacts:
                status = "artifacts_generated"
            reason = {
                "verified": "全新沙箱运行成功，输出与记录的 Flag 一致。",
                "artifacts_generated": "脚本运行成功并已保存图片或音频产物；尚未自动确认其中的 Flag，请人工核对。",
                "needs_review": "EXP 运行失败或未输出记录的 Flag，且没有可核对的媒体产物。",
            }[status]
            replay = {
                "status": status,
                "reason": reason,
                "command": command,
                "exit_code": result.exit_code,
                "stdout": _redact(result.stdout, MAX_EVIDENCE_TEXT),
                "stderr": _redact(result.stderr, MAX_EVIDENCE_TEXT),
                "artifacts": artifacts,
                "artifact_issues": artifact_issues,
            }
            content = (json.dumps(replay, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            relative_log = f"solution/replays/{_digest(content)[:24]}.json"
            atomic_write(safe_path(challenge, relative_log, must_exist=False), content)
            replay["evidence_path"] = relative_log
            return replay
        except Exception as exc:
            return {"status": "needs_review", "reason": f"EXP 复现异常：{_redact(exc, 300)}", "command": command, "exit_code": None, "stdout": "", "stderr": ""}
        finally:
            try:
                await sandbox.stop()
            except Exception as exc:
                logger.warning("Failed to stop EXP replay sandbox: %s", exc)

    def _render(self, record: dict[str, Any], sections: dict[str, Any], replay: dict[str, Any], files: list[Path], challenge: Path,
                *, commands: list[dict[str, Any]] | None = None) -> str:
        if not isinstance(sections, dict):
            raise ValueError("Writeup writer returned invalid sections")
        raw_steps = sections.get("steps") or record["solution_steps"]
        if isinstance(raw_steps, str):
            raw_steps = [raw_steps]
        steps = [_redact(step, 2000) for step in raw_steps if str(step).strip()][:20]
        if not steps:
            steps = [_redact(record["findings_summary"] or "暂无足够步骤材料，需人工补充。", 2000)]
        name = _redact(record["challenge"].get("name") or "Unknown", 200)
        category = _redact(record["challenge"].get("category") or "未分类", 100)
        source = {
            "platform_confirmed": "平台确认", "independent_quorum": "独立复核，未必提交",
            "candidate_found": "候选 Flag（未经确认）",
        }[record["confirmation_source"]]
        replay_label = (
            "未执行复现" if record["confirmation_source"] == "candidate_found" and not replay.get("command")
            else {"verified": "自动复现通过", "manual": "人工复现", "needs_review": "待检查",
                  "artifacts_generated": "产物已生成，待人工核对"}[replay["status"]]
        )
        exp_names = " · ".join(
            f"[{path.relative_to(challenge).as_posix()}]({_link(path.relative_to(challenge).as_posix())})"
            for path in files
        ) or "无"
        evidence = record["evidence"] or ["没有额外证据记录。"]
        command_map = {row["id"]: row for row in commands or []}
        artifact_map = {item["id"]: item for item in validated_artifacts(challenge, record.get("saved_artifacts", ()))}
        used_commands, used_artifacts = set(), set()
        detailed = sections.get("detailed_steps") or []
        for step in detailed:
            if not isinstance(step, dict):
                raise ValueError("Invalid detailed writeup step")
            if set(step.get("evidence_ids", [])) - command_map.keys() or set(step.get("artifact_ids", [])) - artifact_map.keys():
                raise ValueError("Writeup step references evidence that was not supplied")
        command_order = list(dict.fromkeys([
            *(identity for step in detailed[:30] for identity in step.get("evidence_ids", [])), *command_map,
        ]))
        command_numbers = {identity: index for index, identity in enumerate(command_order, 1)}
        artifact_order = list(dict.fromkeys([
            *(identity for step in detailed[:30] for identity in step.get("artifact_ids", [])), *artifact_map,
        ]))
        artifact_titles, artifact_counts = {}, {}
        for identity in artifact_order:
            kind = "图片" if artifact_map[identity]["media_type"].startswith("image/") else "附件"
            artifact_counts[kind] = artifact_counts.get(kind, 0) + 1
            artifact_titles[identity] = f"{kind} {artifact_counts[kind]:02d}"
        source_lines = _exp_source_lines(challenge, files)
        image_count = sum(item["media_type"].startswith("image/") for item in artifact_map.values())
        lines = [
            f"# {name} 题解", "",
            "| 项目 | 内容 |", "| :--- | :--- |",
            f"| 题型 | {_table_cell(category)} |",
            f"| 确认方式 | {_table_cell(source)} |",
            f"| 复现状态 | {_table_cell(replay_label)} |",
            f"| 复现材料 | {len(command_map)} 条命令 · {image_count} 张图片 · {len(artifact_map) - image_count} 个其他产物 |", "",
        ]
        if record["confirmation_source"] == "candidate_found":
            lines += _callout("待确认", "Flag 尚未经过平台或独立验证，以下题解可能需要修订。")
        lines += [
            "**阅读导航**", "",
            "[题目与环境](#01-题目与环境) · [解题思路](#02-解题思路) · [复现步骤](#03-详细复现步骤) · "
            "[EXP](#04-exp-与运行方法) · [结果与 Flag](#05-验证结果与-flag) · [证据附录](#06-证据附录)", "", "---", "",
            "## 01 题目与环境", "", "### 题目描述", "",
        ]
        description = record["challenge"].get("description") or "题目描述未记录。"
        lines += [description, ""]
        lines += ["### 复现环境", ""]
        execution = record.get("execution_environment", {})
        if execution.get("mode") == "local":
            lines += [f"- 本次复现环境：{_redact(execution.get('description'), 1000)}"]
        else:
            lines += [f"- 沙箱镜像：`{record.get('sandbox_image', getattr(self.settings, 'sandbox_image', 'ctf-sandbox'))}`",
                      "- 容器起始目录：`/challenge`；附件目录：`/challenge/distfiles`；可写目录：`/challenge/workspace`。"]
        lines.extend(f"- {_redact(item, 1000)}" for item in sections.get("environment", [])[:12])
        if record["challenge"].get("connection_info"):
            lines += [f"- 题目连接信息：{_redact(record['challenge']['connection_info'], 500)}"]
        lines += [""]
        if execution.get("mode") == "local" and execution.get("cwd"):
            lines += ["**本次实际运行目录**", "", *_code_block(execution["cwd"])]
        if record.get("inputs"):
            lines += ["### 输入附件", "", "| 文件 | 大小（字节） |", "| :--- | ---: |"]
            for item in record["inputs"]:
                lines += [f"| [{_table_cell(item['path'])}]({_link(item['path'])}) | {item['bytes']:,} |"]
            lines += ["", "完整 SHA-256 见文末[文件校验清单](#文件校验清单)。", ""]
        lines += [
            "## 02 解题思路", "",
            _redact(sections.get("principle") or record["findings_summary"] or "原理待补充。", 8000),
            "", "### 解题路线", "",
        ]
        lines.extend(f"{index}. {step}" for index, step in enumerate(steps, 1))
        lines += ["", "## 03 详细复现步骤", ""]
        if detailed:
            for index, step in enumerate(detailed[:30], 1):
                lines += [f"### 步骤 {index:02d} · {_redact(step.get('title'), 200)}", "", _redact(step.get("explanation"), 6000), ""]
                for identity in step.get("evidence_ids", []):
                    if identity not in used_commands:
                        lines += _command_lines(command_map[identity], command_numbers[identity])
                        used_commands.add(identity)
                    else:
                        lines += [f"[命令与实际输出]({_heading_ref(f'命令记录 {command_numbers[identity]:02d}')})", ""]
                for identity in step.get("artifact_ids", []):
                    if identity not in used_artifacts:
                        lines += _artifact_lines(artifact_map[identity], artifact_titles[identity])
                        used_artifacts.add(identity)
                    else:
                        lines += [f"[查看证据产物]({_heading_ref(artifact_titles[identity])})", ""]
                if step.get("expected_result"):
                    lines += _callout("核对要点", step["expected_result"])
        else:
            lines += ["逐步说明尚未结构化；实际保留的命令与产物见[证据附录](#06-证据附录)。", ""]
        lines += ["", "## 04 EXP 与运行方法", "", f"**脚本文件**：{exp_names}", ""]
        if sections.get("exp_usage"):
            lines += [_redact(sections["exp_usage"], 4000), ""]
        elif replay.get("command"):
            lines += _code_block(replay["command"], "powershell" if replay.get("execution_mode") == "local" else "bash")
        else:
            lines += ["按上述步骤人工复现。", ""]
        if source_lines:
            lines += ["完整代码见文末的 [EXP 源码](#07-exp-源码)。", ""]
        lines += ["", "## 05 验证结果与 Flag", ""]
        lines += _callout("复现结论", replay["reason"], 1000)
        replay_lines = []
        if replay.get("command"):
            replay_lines += ["**实际运行命令**", "", *_code_block(replay["command"], "powershell" if replay.get("execution_mode") == "local" else "bash")]
        if replay.get("exit_code") is not None:
            replay_lines += [f"退出码：`{replay['exit_code']}`", ""]
        for key, label in (("stdout", "标准输出"), ("stderr", "标准错误")):
            if replay.get(key):
                replay_lines += [f"**{label}**", "", *_code_block(replay[key])]
        if replay.get("evidence_path"):
            replay_lines += [f"[查看完整复现记录]({_link(replay['evidence_path'])})", ""]
        if replay_lines:
            lines += ["[查看复现命令与输出](#复现记录)", ""]
        lines += ["### Flag", "", *_code_block(record["flag"]), "### 限制与备注", "",
                  _redact(sections.get("limitations") or "暂无。", 4000), ""]
        lines.extend(f"- {_redact(issue, 500)}" for issue in record.get("artifact_issues", []))
        lines += ["", "## 06 证据附录", ""]
        remaining_artifacts = [item for identity, item in artifact_map.items() if identity not in used_artifacts]
        if remaining_artifacts:
            lines += ["### 补充产物", ""]
            for artifact in remaining_artifacts:
                lines += _artifact_lines(artifact, artifact_titles[artifact["id"]])
        lines += ["### 补充证据说明", "", *(f"- {_redact(item, 1000)}" for item in evidence[:12]), ""]
        hashes = []
        for label, items in (("输入附件", record.get("inputs", [])), ("证据产物", artifact_map.values())):
            for item in items:
                hashes += [f"**{label}** · [{item['path']}]({_link(item['path'])})", "",
                           f"SHA-256：`{item['sha256']}`", ""]
        if hashes:
            lines += ["### 文件校验清单", "", *hashes]
        if replay_lines:
            lines += ["### 复现记录", "", *replay_lines]
        if command_order:
            lines += ["### 命令与输出记录", ""]
            for identity in command_order:
                lines += _command_lines(command_map[identity], command_numbers[identity], appendix=True)
        if source_lines:
            lines += ["## 07 EXP 源码", "", *source_lines]
        lines += ["---", "", f"[返回顶部]({_heading_ref(f'{name} 题解')})", ""]
        return "\n".join(lines)

    async def wait_for_pending(self, timeout: float = 180) -> None:
        tasks = [task for task in self._tasks.values() if not task.done()]
        if tasks:
            await asyncio.wait(tasks, timeout=max(0, timeout))

    async def resume_pending(self, challenges_root: str | Path) -> None:
        root = Path(challenges_root)
        if not root.is_dir():
            return
        for path in root.rglob("solution/manifest.json"):
            try:
                manifest = _read_manifest(path)
                current = next((item for item in manifest["records"] if item.get("key") == manifest.get("current_key")), None)
                if current and current.get("status") in {"pending", "failed"}:
                    configured_model = getattr(self.settings, "writeup_model_spec", "")
                    if configured_model and current.get("model_spec") != configured_model:
                        current["model_spec"] = configured_model
                        current["updated_at"] = _now()
                        _atomic_json(path, manifest)
                    self._schedule(path.parent.parent)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                logger.warning("Cannot resume writeup at %s: %s", path, exc)
