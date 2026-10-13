"""Historical writeup backfill for flag candidates and confirmations in one run."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import click

from backend.config import Settings
from backend.models import DEFAULT_MODELS, model_id_from_spec
from backend.prompts import ChallengeMeta
from backend.solver_base import SolverResult
from backend.writeups import SOURCE_PRIORITY, WriteupManager

_SOURCE_VALUES = set(SOURCE_PRIORITY)
_RUN_ID = re.compile(r"^[A-Za-z0-9_-]+$")
_CORRECT_DISPLAY = re.compile(r'^CORRECT\s*[—:\-]\s*.*?["“](.+?)["”]', re.I | re.S)


@dataclass(frozen=True)
class BackfillCandidate:
    challenge_dir: Path
    meta: ChallengeMeta
    flag: str
    source: str
    model_spec: str
    evidence: tuple[str, ...]
    solution_steps: tuple[str, ...] = ()
    findings_summary: str = ""
    verified_by: tuple[str, ...] = ()
    from_manifest: bool = False
    record_status: str = ""


def _jsonl(path: Path):
    try:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    yield event
    except OSError:
        return


def _args(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def _result_text(value: Any) -> str:
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value
        return _result_text(decoded)
    if isinstance(value, list):
        return "\n".join(_result_text(item) for item in value)
    if isinstance(value, dict):
        for key in ("content", "result", "text", "display"):
            if key in value:
                return _result_text(value[key])
    return ""


def _material_available(*groups: Any) -> bool:
    """Require at least one substantive explanation, evidence, or saved EXP."""
    for group in groups:
        values = group if isinstance(group, (list, tuple)) else (group,)
        if any(len(str(value).strip()) >= 18 for value in values if value):
            return True
    return False


def _saved_file_exists(challenge_dir: Path, raw: str) -> bool:
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != ".writeup-drafts":
        return False
    local = challenge_dir.joinpath(*path.parts)
    try:
        cursor = challenge_dir
        for part in path.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return False
        return local.is_file() and local.resolve().is_relative_to(challenge_dir.resolve())
    except OSError:
        return False


def _challenge_index(root: Path) -> tuple[dict[str, tuple[Path, ChallengeMeta]], list[str]]:
    found: dict[str, tuple[Path, ChallengeMeta]] = {}
    skipped: list[str] = []
    for path in sorted(root.rglob("metadata.yml")) if root.exists() else []:
        try:
            meta = ChallengeMeta.from_yaml(path)
        except Exception as exc:
            skipped.append(f"{path.parent}: metadata.yml 无法读取：{exc}")
            continue
        entry = (path.parent, meta)
        found[meta.name] = entry
        if meta.native_id:
            found[meta.native_id] = entry
    return found, skipped


def _coordinator_confirmations(
    run_id: str, log_dir: Path
) -> tuple[dict[tuple[str, str], str], list[str]]:
    """Return exact challenge/flag acceptances from this run's coordinator log."""
    confirmed: dict[tuple[str, str], str] = {}
    skipped: list[str] = []
    files = sorted(
        path for path in log_dir.glob("coordinator-*.jsonl")
        if path.name.startswith(f"coordinator-{run_id}-")
    ) if log_dir.exists() else []
    if not files:
        skipped.append(f"运行 {run_id}: 未找到对应的 coordinator 日志")
    for path in files:
        pending: list[tuple[str, dict[str, Any]]] = []
        for event in _jsonl(path):
            tool = str(event.get("tool", "")).rsplit("__", 1)[-1]
            if tool not in {"submit_flag", "confirm_submission"}:
                continue
            if event.get("type") == "tool_call":
                pending.append((tool, _args(event.get("args"))))
            elif event.get("type") == "tool_result":
                pair_index = next((i for i in range(len(pending) - 1, -1, -1) if pending[i][0] == tool), None)
                if pair_index is None:
                    continue
                _, call = pending.pop(pair_index)
                challenge = str(call.get("challenge_name") or "")
                flag = str(call.get("flag") or "").strip()
                if not challenge or not flag:
                    continue
                if tool == "confirm_submission" and call.get("accepted") is not True:
                    continue
                display = _result_text(event.get("result"))
                match = _CORRECT_DISPLAY.search(display.strip())
                if not match or match.group(1) != flag:
                    continue
                reason = str(call.get("reason") or "")
                confirmed[(challenge, flag)] = reason
    return confirmed, skipped


def _trace_evidence(
    root: Path, challenge_name: str, flag: str, run_id: str
) -> tuple[str, tuple[str, ...]] | None:
    """Read method evidence only from an exact confirmed finish for this flag.

    Old traces lack run IDs.  They are used only after the coordinator log has
    independently confirmed the same challenge and flag for the selected run.
    """
    for path in sorted(root.glob("trace-*.jsonl")) if root.exists() else []:
        start: dict[str, Any] | None = None
        finish: dict[str, Any] | None = None
        snippets: list[str] = []
        for event in _jsonl(path):
            kind = event.get("type")
            if kind == "start":
                start = event
            elif kind == "finish":
                finish = event
            elif kind == "model_response" and event.get("text"):
                snippets.append(str(event["text"])[:800])
            elif kind == "tool_result" and event.get("result"):
                snippets.append(str(event["result"])[:800])
        if not start or not finish:
            continue
        if start.get("challenge") != challenge_name:
            continue
        if finish.get("flag") != flag or finish.get("confirmed") is not True:
            continue
        if finish.get("status") != "flag_found":
            continue
        if (start.get("run_id") or finish.get("run_id")) not in {None, "", run_id}:
            continue
        model_id = str(start.get("model") or "")
        model_spec = next((spec for spec in DEFAULT_MODELS if model_id_from_spec(spec) == model_id), "")
        selected = tuple(dict.fromkeys(snippets[-8:]))
        return model_spec, selected
    return None


def _run_scoped_traces(
    run_id: str, log_dir: Path, challenges: dict[str, tuple[Path, ChallengeMeta]]
) -> tuple[list[BackfillCandidate], list[str]]:
    """Use only solver traces explicitly stamped with the selected run ID."""
    accepted: list[BackfillCandidate] = []
    skipped: list[str] = []
    files = sorted(log_dir.glob("trace-*.jsonl")) if log_dir.exists() else []
    for path in files:
        start: dict[str, Any] | None = None
        finish: dict[str, Any] | None = None
        snippets: list[str] = []
        for event in _jsonl(path):
            kind = event.get("type")
            if kind == "start":
                start = event
            elif kind == "finish":
                finish = event
            elif kind == "model_response" and event.get("text"):
                snippets.append(str(event["text"])[:800])
            elif kind == "tool_result" and event.get("result"):
                snippets.append(str(event["result"])[:800])
        if not start or not finish:
            continue
        if start.get("run_id") != run_id or finish.get("run_id") != run_id:
            continue
        challenge_name = str(start.get("challenge") or "")
        entry = challenges.get(challenge_name)
        if not entry:
            skipped.append(f"{challenge_name or path.name}: 已确认 trace 没有对应题目包")
            continue
        flag = str(finish.get("flag") or "")
        status = str(finish.get("status") or "")
        if status not in {"flag_found", "candidate_found"}:
            continue
        source = "platform_confirmed" if status == "flag_found" and finish.get("confirmed") is True else "candidate_found"
        if not flag or flag != flag.strip() or not _material_available(snippets):
            skipped.append(f"{challenge_name}: trace 缺少精确 Flag 或解题证据")
            continue
        challenge_dir, meta = entry
        model_id = str(start.get("model") or "")
        model_spec = next((spec for spec in DEFAULT_MODELS if model_id_from_spec(spec) == model_id), "")
        accepted.append(BackfillCandidate(
            challenge_dir, meta, flag, source, model_spec,
            tuple(dict.fromkeys(snippets[-8:])),
            findings_summary=snippets[-1] if snippets else "",
        ))
    return accepted, skipped


def discover_candidates(
    run_id: str, challenges_dir: Path, logs_dir: Path
) -> tuple[list[BackfillCandidate], list[str]]:
    """Find run-scoped candidates and confirmations with solution evidence."""
    challenges, skipped = _challenge_index(challenges_dir)
    entries = {entry[0]: entry for entry in challenges.values()}
    confirmations, log_skips = _coordinator_confirmations(run_id, logs_dir)
    skipped.extend(log_skips)
    candidates: dict[tuple[Path, str], BackfillCandidate] = {}

    scoped_traces, trace_skips = _run_scoped_traces(run_id, logs_dir, challenges)
    skipped.extend(trace_skips)
    for candidate in scoped_traces:
        candidates[(candidate.challenge_dir, candidate.flag)] = candidate

    for challenge_dir, meta in entries.values():
        manifest_path = challenge_dir / "solution" / "manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            records = manifest.get("records", [])
            if not isinstance(records, list):
                raise ValueError("records must be a list")
        except (OSError, ValueError) as exc:
            skipped.append(f"{meta.name}: 状态清单无效：{exc}")
            continue
        for record in records:
            if not isinstance(record, dict) or record.get("run_id") != run_id:
                continue
            flag = str(record.get("flag") or "")
            source = str(record.get("confirmation_source") or "")
            if not flag or flag != flag.strip() or source not in _SOURCE_VALUES:
                skipped.append(f"{meta.name}: 状态清单缺少有效来源或精确 Flag")
                continue
            evidence = tuple(str(x) for x in record.get("evidence") or ())
            steps = tuple(str(x) for x in record.get("solution_steps") or ())
            summary = str(record.get("findings_summary") or "")
            saved = tuple(str(x) for x in record.get("saved_exp_paths") or ())
            saved_files = tuple(raw for raw in saved if _saved_file_exists(challenge_dir, raw))
            if not _material_available(evidence, steps, summary) and not saved_files:
                skipped.append(f"{meta.name}: 缺少解题证据，跳过")
                continue
            verified_by = tuple(str(x) for x in record.get("verified_by") or ())
            if source == "independent_quorum" and len(set(verified_by)) < 2:
                skipped.append(f"{meta.name}: 清单未保存独立复核来源，跳过")
                continue
            previous = candidates.get((challenge_dir, flag))
            if previous and SOURCE_PRIORITY[previous.source] > SOURCE_PRIORITY[source]:
                continue
            candidates[(challenge_dir, flag)] = BackfillCandidate(
                challenge_dir, meta, flag, source,
                str(record.get("model_spec") or ""), evidence, steps, summary,
                verified_by, True, str(record.get("status") or ""),
            )

    for (challenge_name, flag), reason in confirmations.items():
        entry = challenges.get(challenge_name)
        if not entry:
            skipped.append(f"{challenge_name}: 平台确认存在，但没有对应题目包")
            continue
        challenge_dir, meta = entry
        prior = candidates.get((challenge_dir, flag))
        if prior and prior.source == "platform_confirmed":
            continue
        trace = _trace_evidence(logs_dir, meta.name, flag, run_id)
        model_spec, snippets = trace if trace else ("", ())
        evidence = tuple(dict.fromkeys((*(prior.evidence if prior else ()), *snippets, reason))) if reason else tuple(
            dict.fromkeys((*(prior.evidence if prior else ()), *snippets))
        )
        if not _material_available(evidence, prior.solution_steps if prior else ()):
            skipped.append(f"{meta.name}: 平台确认存在，但缺少可用解题证据")
            continue
        candidates[(challenge_dir, flag)] = BackfillCandidate(
            challenge_dir, meta, flag, "platform_confirmed", model_spec or (prior.model_spec if prior else ""),
            evidence, solution_steps=prior.solution_steps if prior else (),
            findings_summary=snippets[-1] if snippets else (prior.findings_summary if prior else ""),
            from_manifest=bool(prior and prior.from_manifest),
            record_status="pending" if prior and prior.source != "platform_confirmed" else (prior.record_status if prior else ""),
        )

    # Only run-scoped trace candidates and exact coordinator confirmations are
    # considered. Unscoped guesses and external solve status are ignored.
    return list(candidates.values()), skipped


def _current_writeup_source(challenge_dir: Path) -> str:
    path = challenge_dir / "solution" / "manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        record = next(
            (item for item in manifest.get("records", [])
             if item.get("key") == manifest.get("current_key")),
            None,
        )
        return str(record.get("confirmation_source") or "") if record else ""
    except (OSError, ValueError, TypeError):
        return ""


async def run_backfill(
    run_id: str,
    challenges_dir: Path,
    logs_dir: Path,
    *,
    model_spec: str = "",
    force: bool = False,
) -> tuple[int, list[str]]:
    settings = Settings()
    settings.challenge_run_id = run_id
    if model_spec:
        settings.writeup_model_spec = model_spec
    default_model = settings.writeup_model_spec or (
        f"openai/{settings.model_name}" if settings.model_name else DEFAULT_MODELS[0]
    )
    manager = WriteupManager(settings, default_model_spec=default_model)
    candidates, messages = discover_candidates(run_id, challenges_dir, logs_dir)
    scheduled = 0
    for candidate in candidates:
        writeup = candidate.challenge_dir / "writeup.md"
        current_source = _current_writeup_source(candidate.challenge_dir)
        upgrade = SOURCE_PRIORITY[candidate.source] > SOURCE_PRIORITY.get(current_source, -1)
        if writeup.exists() and not force and candidate.record_status not in {"pending", "failed"} and not upgrade:
            messages.append(f"{candidate.meta.name}: 已有 writeup.md，保持原样")
            continue
        solver_result = None
        if candidate.from_manifest or candidate.solution_steps or candidate.findings_summary:
            solver_result = SolverResult(
                flag=candidate.flag,
                status={"independent_quorum": "verified", "platform_confirmed": "flag_found",
                        "candidate_found": "candidate_found"}[candidate.source],
                findings_summary=candidate.findings_summary,
                step_count=0,
                cost_usd=0.0,
                log_path="",
                evidence=candidate.evidence,
                verified_by=candidate.verified_by,
                solution_steps=candidate.solution_steps,
                model_spec=candidate.model_spec,
            )
        result = await manager.record_and_schedule(
            candidate.challenge_dir,
            candidate.meta,
            candidate.flag,
            candidate.source,
            solver_result=solver_result,
            model_spec=model_spec or candidate.model_spec or default_model,
            evidence=() if solver_result else candidate.evidence,
            force=force,
        )
        if result is None:
            messages.append(f"{candidate.meta.name}: Flag 记录无效，跳过")
        else:
            scheduled += 1
            messages.append(f"{candidate.meta.name}: 已安排生成中文题解")
    await manager.wait_for_pending(
        timeout=max(
            1,
            int(settings.writeup_timeout_seconds)
            + int(settings.writeup_replay_timeout_seconds)
            + 90,
        )
    )
    return scheduled, messages


@click.group()
def main() -> None:
    """Generate Chinese CTF writeups from flag candidates and confirmations."""


@main.command()
@click.option("--run-id", required=True, help="Existing competition run ID")
@click.option("--model", "model_spec", default="", help="Override provider/model for writing")
@click.option("--force", is_flag=True, help="Regenerate existing writeups, including manual edits")
@click.option("--challenges-dir", type=click.Path(path_type=Path), default=Path("challenges"))
@click.option("--logs-dir", type=click.Path(path_type=Path), default=Path("logs"))
def backfill(
    run_id: str, model_spec: str, force: bool, challenges_dir: Path, logs_dir: Path
) -> None:
    """Backfill one run; candidate writeups are marked unverified."""
    if not _RUN_ID.fullmatch(run_id):
        raise click.BadParameter("run ID 只能包含字母、数字、下划线和连字符", param_hint="--run-id")
    if model_spec and "/" not in model_spec:
        raise click.BadParameter("模型必须使用 provider/model 格式", param_hint="--model")
    scheduled, messages = asyncio.run(
        run_backfill(run_id, challenges_dir, logs_dir, model_spec=model_spec, force=force)
    )
    for message in messages:
        click.echo(message)
    click.echo(f"已安排 {scheduled} 道题生成中文题解。")
