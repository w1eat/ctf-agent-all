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
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from backend.sandbox import DockerSandbox

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
    text = _short(value, limit)
    text = re.sub(r"(?i)\bBearer\s+[^\s'\"`]+", "Bearer [已脱敏]", text)
    text = re.sub(
        r"(?im)\b(Authorization|Cookie|Set-Cookie)\s*:\s*[^\r\n]+",
        lambda m: f"{m.group(1)}: [已脱敏]",
        text,
    )
    text = re.sub(
        r"(?i)\b([\w-]*(?:api[_-]?key|access[_-]?key|token|password|passwd|secret|username|account))"
        r"(\s*[=:]\s*['\"]?)([^\s,'\"}\]]+)",
        lambda m: f"{m.group(1)}{m.group(2)}[已脱敏]",
        text,
    )
    text = re.sub(r"(?i)\bsk-[A-Za-z0-9_-]{12,}\b", "[已脱敏密钥]", text)
    text = re.sub(r"\b[A-Z0-9]{20}\b", lambda m: "[已脱敏密钥]" if m.group().startswith("AKIA") else m.group(), text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[已脱敏邮箱]", text)
    text = re.sub(r"(?i)(https?://)[^\s/@:]+:[^\s/@]+@", r"\1[已脱敏账号]@", text)
    return text


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


def _saved_exp_paths(result: Any, challenge: Path, flag: str) -> list[str]:
    supplied = (
        _value(result, "saved_exp_paths", None)
        or _value(result, "exp_files", None)
        or _value(result, "exp_paths", None)
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


class WriteupManager:
    """Persists flag candidates and confirmations before launching writeup jobs."""

    def __init__(self, settings: Any, default_model_spec: str = "") -> None:
        self.settings = settings
        self.default_model_spec = default_model_spec
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
        if existing and existing.get("status") in {"complete", "needs_review"} and not force and writeup_path.exists() and not manual_edit:
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
            "saved_exp_paths": _saved_exp_paths(solver_result, challenge, flag) or (list(previous.get("saved_exp_paths", ())) if previous else []),
            "exp_run_command": _safe_run_command(_value(solver_result, "exp_run_command", "") or (previous.get("exp_run_command", "") if previous else ""), flag),
            "status": "needs_review" if manual_edit else "pending",
            "replay": {},
            "writeup_sha256": None,
            "planned_sha256": None,
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
        processed: set[str] = set()
        while True:
            manifest = _read_manifest(manifest_path)
            key = manifest.get("current_key", "")
            record = next((item for item in manifest["records"] if item.get("key") == key), None)
            if not record or key in processed or record.get("status") not in {"pending", "failed"}:
                return
            processed.add(key)
            try:
                await self._generate(challenge, record, force=force)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Writeup generation failed for %s: %s", challenge, exc, exc_info=True)
                latest = _read_manifest(manifest_path)
                matching = next((item for item in latest["records"] if item.get("key") == key), None)
                if matching:
                    matching["status"] = "failed"
                    matching["error"] = _redact(exc, 500)
                    matching["updated_at"] = _now()
                    if latest.get("current_key") == key:
                        latest["status"] = "failed"
                    _atomic_json(manifest_path, latest)

    async def _generate(self, challenge: Path, record: dict[str, Any], *, force: bool) -> None:
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
        context = {
            "challenge": record["challenge"],
            "confirmation_source": record["confirmation_source"],
            "flag": record["flag"],
            "findings_summary": record["findings_summary"],
            "solution_steps": record["solution_steps"],
            "evidence": record["evidence"],
            "exp_files": [
                {"path": path.relative_to(challenge).as_posix(), "content": _redact(path.read_text(encoding="utf-8", errors="replace"), 6000)}
                for path in exp_files
            ],
            "replay": replay,
        }
        has_method = bool(record["findings_summary"] or record["solution_steps"] or record["saved_exp_paths"])
        if has_method:
            timeout = max(1, int(getattr(self.settings, "writeup_timeout_seconds", 180) or 180))
            logger.info("Generating writeup for %s with %s", challenge, record["model_spec"])
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
        markdown = self._render(record, sections, replay, exp_files, challenge)
        digest = _digest(markdown)
        latest = _read_manifest(manifest_path)
        key = record["key"]
        if latest.get("current_key") != key:
            return
        target = next(item for item in latest["records"] if item.get("key") == key)
        writeup = challenge / "writeup.md"
        if writeup.exists() and not force and not _file_matches_known_hash(writeup, latest):
            target["status"] = latest["status"] = "needs_review"
            target["error"] = "检测到人工修改的 writeup.md，已保留原文件。"
            _atomic_json(manifest_path, latest)
            return
        target["planned_sha256"] = digest
        target["replay"] = replay
        _atomic_json(manifest_path, latest)
        _atomic_bytes(writeup, markdown.encode("utf-8"))
        target["status"] = latest["status"] = (
            "needs_review" if replay["status"] == "needs_review" or not has_method else "complete"
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
            status = "verified" if result.exit_code == 0 and exact else "needs_review"
            reason = "全新沙箱运行成功，输出与记录的 Flag 一致。" if status == "verified" else "EXP 运行失败或未输出记录的 Flag。"
            return {
                "status": status,
                "reason": reason,
                "command": command,
                "exit_code": result.exit_code,
                "stdout": _redact(result.stdout, 2000),
                "stderr": _redact(result.stderr, 1000),
            }
        except Exception as exc:
            return {"status": "needs_review", "reason": f"EXP 复现异常：{_redact(exc, 300)}", "command": command, "exit_code": None, "stdout": "", "stderr": ""}
        finally:
            try:
                await sandbox.stop()
            except Exception as exc:
                logger.warning("Failed to stop EXP replay sandbox: %s", exc)

    def _render(self, record: dict[str, Any], sections: dict[str, Any], replay: dict[str, Any], files: list[Path], challenge: Path) -> str:
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
            "platform_confirmed": "平台确认",
            "independent_quorum": "独立复核，未必提交",
            "candidate_found": "候选 Flag（未经确认）",
        }[record["confirmation_source"]]
        replay_label = (
            "未执行复现" if record["confirmation_source"] == "candidate_found"
            else {"verified": "自动复现通过", "manual": "人工复现", "needs_review": "待检查"}[replay["status"]]
        )
        exp_names = ", ".join(f"`{path.relative_to(challenge).as_posix()}`" for path in files) or "无"
        evidence = record["evidence"] or ["没有额外证据记录。"]
        lines = [
            f"# {name} 题解", "", f"- 分类：{category}", f"- 确认方式：{source}",
            f"- 复现状态：{replay_label}",
            "- 注意：Flag 尚未经过平台或独立验证，以下题解可能需要修订。"
            if record["confirmation_source"] == "candidate_found" else "",
            "", "## 题目信息", "",
            record["challenge"].get("description") or "题目描述未记录。", "",
            "## 解题原理", "", _redact(sections.get("principle") or record["findings_summary"] or "原理待补充。", 4000),
            "", "## 关键步骤", "",
        ]
        lines.extend(f"{index}. {step}" for index, step in enumerate(steps, 1))
        lines += ["", "## EXP 与运行方法", "", f"文件：{exp_names}", "", _redact(sections.get("exp_usage") or replay["command"] or "按上述步骤人工复现。", 2000), "", "## 验证结果", "", _redact(replay["reason"], 1000)]
        if replay.get("command"):
            lines += ["", f"运行命令：`{replay['command']}`"]
        lines += ["", "证据：", ""]
        lines.extend(f"- {_redact(item, 1000)}" for item in evidence[:12])
        lines += ["", "## Flag", "", f"`{record['flag']}`", "", "## 限制与备注", "", _redact(sections.get("limitations") or "暂无。", 2000), ""]
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
