"""Shared coordinator tool logic — called by both Claude SDK and Codex coordinators."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path

from backend.deps import CoordinatorDeps
from backend.prompts import ChallengeMeta
from backend.solver_base import CANDIDATE_FOUND, FLAG_FOUND, VERIFIED

logger = logging.getLogger(__name__)


async def do_coordinator_shell(
    deps: CoordinatorDeps,
    command: str,
    cwd: str = "",
    timeout_seconds: float = 120,
) -> str:
    """Run a host shell command when full Coordinator access is enabled."""
    if not bool(getattr(deps.settings, "coordinator_full_access", False)):
        return "Coordinator full access is disabled. Start with --coordinator-full-access."
    if not command.strip():
        return "Shell command is empty."

    workdir = str(Path(cwd).expanduser().resolve()) if cwd else str(Path.cwd())
    if not Path(workdir).is_dir():
        return f"Shell cwd does not exist or is not a directory: {workdir}"

    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        timeout = 120.0
    timeout = max(0.0, timeout)

    started = time.monotonic()
    process = None
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=workdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        communicate = process.communicate()
        if timeout:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(communicate, timeout=timeout)
        else:
            stdout_bytes, stderr_bytes = await communicate
        stdout = stdout_bytes.decode(errors="replace")
        stderr = stderr_bytes.decode(errors="replace")
        exit_code = process.returncode
    except TimeoutError:
        timed_out = True
        if process is not None:
            process.kill()
            stdout_bytes, stderr_bytes = await process.communicate()
            stdout = stdout_bytes.decode(errors="replace")
            stderr = stderr_bytes.decode(errors="replace")
            exit_code = process.returncode
    except Exception as exc:
        stderr = f"{type(exc).__name__}: {exc}"

    duration = time.monotonic() - started
    if deps.tracer:
        deps.tracer.shell_result(
            command=command,
            cwd=workdir,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            timed_out=timed_out,
        )

    return "\n".join(
        [
            f"cwd: {workdir}",
            f"exit_code: {exit_code}",
            f"timed_out: {timed_out}",
            "stdout:",
            stdout or "(empty)",
            "stderr:",
            stderr or "(empty)",
        ]
    )[:50000]


async def do_fetch_challenges(deps: CoordinatorDeps) -> str:
    challenges = await deps.platform.list_challenges()
    solved = await deps.platform.get_solve_status()
    result = [
        {
            "id": ch.native_id,
            "name": ch.name,
            "category": ch.category or "?",
            "value": ch.points,
            "mode": ch.mode.value,
            "state": getattr(ch.state, "value", str(getattr(ch, "state", "discovered"))),
            "status": "SOLVED" if ch.name in solved else "unsolved",
            "has_files": bool(ch.files),
            "has_attachments": bool(ch.files or ch.source_data.get("attachments")),
            "environment_required": bool(
                getattr(ch, "environment_required", False)
                or ch.connection_info
                or ch.environment
                or ch.source_data.get("environment_required")
            ),
            "connection_info": bool(ch.connection_info),
            "description": ch.description[:200],
        }
        for ch in challenges
    ]
    return json.dumps(result, indent=2)


async def do_get_solve_status(deps: CoordinatorDeps) -> str:
    solved = await deps.platform.get_solve_status()
    swarm_status = {name: swarm.get_status() for name, swarm in deps.swarms.items()}
    return json.dumps(
        {
            "solved": sorted(solved),
            "active_swarms": swarm_status,
            "pending_challenges": deps.pending_challenges,
        },
        indent=2,
    )


async def do_spawn_swarm(deps: CoordinatorDeps, challenge_name: str) -> str:
    from backend.submission_setup import submission_setup_issue

    issue = submission_setup_issue(deps)
    if issue:
        return f"Submission setup required before spawning {challenge_name}: {issue}. Call save_recipe first."

    # Retire ALL finished swarms before checking capacity
    finished = [
        name for name in deps.swarms
        if name in deps.swarm_tasks and deps.swarm_tasks[name].done()
    ]
    for name in finished:
        del deps.swarms[name]
        deps.swarm_tasks.pop(name, None)

    active_count = len(deps.swarms)
    if active_count >= deps.max_concurrent_challenges:
        return f"At capacity ({active_count}/{deps.max_concurrent_challenges} challenges running). Wait for one to finish."

    if challenge_name in deps.swarms:
        return f"Swarm still running for {challenge_name}"

    # Prepare the normalized challenge package if needed.
    if challenge_name not in deps.challenge_dirs:
        challenges = await deps.platform.list_challenges()
        bundle = next((c for c in challenges if c.name == challenge_name or c.native_id == challenge_name), None)
        if not bundle:
            return f"Challenge '{challenge_name}' not found on the configured platform"
        prepared = await deps.platform.prepare_challenge(bundle.native_id)
        challenge_name = prepared.name
        try:
            package_state = await deps.platform.get_challenge_state(challenge_name)
        except Exception as exc:
            deps.pending_challenges[challenge_name] = str(exc)
            deps.pending_since.setdefault(challenge_name, time.monotonic())
            return f"Waiting for challenge package {challenge_name}: {exc}"
        ch_dir = str(package_state.get("package_dir") or Path(deps.challenges_root) / re_slug(challenge_name))
        meta_path = Path(ch_dir) / "metadata.yml"
        if not meta_path.exists():
            return f"Platform prepared '{prepared.name}' but did not create metadata.yml"
        deps.challenge_dirs[challenge_name] = ch_dir
        deps.challenge_metas[challenge_name] = ChallengeMeta.from_yaml(meta_path)

    deps.selected_challenges.add(challenge_name)

    state_getter = getattr(deps.platform, "get_challenge_state", None)
    if state_getter:
        try:
            package_state = await state_getter(challenge_name)
        except Exception as exc:
            deps.pending_challenges[challenge_name] = str(exc)
            deps.pending_since.setdefault(challenge_name, time.monotonic())
            return f"Waiting for challenge package {challenge_name}: {exc}"
        if package_state.get("state") != "ready":
            reason = package_state.get("reason") or "challenge package is not ready"
            deps.pending_challenges[challenge_name] = reason
            deps.pending_since.setdefault(challenge_name, time.monotonic())
            return f"Waiting for challenge package {challenge_name}: {reason}"
        deps.pending_challenges.pop(challenge_name, None)
        deps.pending_since.pop(challenge_name, None)
        meta = deps.challenge_metas[challenge_name]
        meta.connection_info = package_state.get("connection_info") or meta.connection_info
        meta.environment = package_state.get("environment") or meta.environment

    from backend.agents.swarm import ChallengeSwarm

    if deps.analysis_gateway:
        await deps.analysis_gateway.register_challenge(
            challenge_name, deps.challenge_dirs[challenge_name]
        )

    swarm = ChallengeSwarm(
        challenge_dir=deps.challenge_dirs[challenge_name],
        meta=deps.challenge_metas[challenge_name],
        platform=deps.platform,
        cost_tracker=deps.cost_tracker,
        settings=deps.settings,
        model_specs=deps.model_specs,
        no_submit=deps.no_submit,
        coordinator_inbox=deps.coordinator_inbox,
        analysis_gateway=deps.analysis_gateway,
        writeup_manager=deps.writeup_manager,
    )
    deps.swarms[challenge_name] = swarm

    async def _run_and_cleanup() -> None:
        try:
            result = await swarm.run()
            if result and result.flag and result.status in (CANDIDATE_FOUND, FLAG_FOUND, VERIFIED):
                getter = getattr(deps.platform, "get_confirmed_flag", None)
                platform_flag = getter(challenge_name) if callable(getter) else None
                recorded = deps.results.get(challenge_name, {})
                recorded_flag = (
                    recorded.get("flag") if recorded.get("submit") == "platform confirmed" else None
                )
                exact_confirmed = swarm.confirmed_flag or platform_flag or recorded_flag
                if exact_confirmed and result.flag.strip() != exact_confirmed:
                    logger.warning(
                        "Solver flag mismatch for %s; retaining platform-confirmed value",
                        challenge_name,
                    )
                    if recorded_flag != exact_confirmed:
                        await _record_coordinator_confirmation(
                            deps, challenge_name, exact_confirmed, "Exact browser submission confirmation"
                        )
                    return
                source = "candidate_found"
                if exact_confirmed:
                    source = "platform_confirmed"
                elif result.status == VERIFIED:
                    quorum = int(getattr(deps.settings, "flag_verification_quorum", 2) or 2)
                    if len(result.verified_by) >= quorum:
                        source = "independent_quorum"
                deps.results[challenge_name] = {
                    "flag": result.flag,
                    "submit": {
                        "platform_confirmed": "platform confirmed",
                        "independent_quorum": "independently verified",
                        "candidate_found": "candidate (unverified)",
                    }[source],
                }
                if deps.writeup_manager:
                    try:
                        await deps.writeup_manager.record_and_schedule(
                            deps.challenge_dirs[challenge_name],
                            deps.challenge_metas[challenge_name],
                            result.flag,
                            source,
                            solver_result=result,
                            model_spec=(
                                getattr(deps.settings, "writeup_model_spec", "")
                                or result.model_spec
                                or deps.model_specs[0]
                            ),
                        )
                    except Exception:
                        logger.exception("Could not queue writeup for %s", challenge_name)
        finally:
            if deps.analysis_gateway:
                await deps.analysis_gateway.release_challenge(challenge_name)

    task = asyncio.create_task(_run_and_cleanup(), name=f"swarm-{challenge_name}")
    deps.swarm_tasks[challenge_name] = task
    deps.reported_finished_swarms.discard(challenge_name)
    return f"Swarm spawned for {challenge_name} with {len(deps.model_specs)} models"


async def do_check_swarm_status(deps: CoordinatorDeps, challenge_name: str) -> str:
    swarm = deps.swarms.get(challenge_name)
    if not swarm:
        return f"No swarm running for {challenge_name}"
    return json.dumps(swarm.get_status(), indent=2)


async def do_submit_flag(deps: CoordinatorDeps, challenge_name: str, flag: str) -> str:
    if deps.no_submit:
        return f'DRY RUN — would submit "{flag.strip()}" for {challenge_name}'
    try:
        result = await deps.platform.submit_flag(challenge_name, flag)
        if result.status in {"correct", "already_solved"}:
            await _record_coordinator_confirmation(deps, challenge_name, flag, result.display)
        return result.display
    except Exception as e:
        return f"submit_flag error: {e}"


async def do_confirm_submission(
    deps: CoordinatorDeps, challenge_name: str, flag: str, accepted: bool, reason: str
) -> str:
    if deps.no_submit:
        return "DRY RUN — submission confirmation is disabled because --no-submit is set."
    try:
        result = await deps.platform.confirm_submission(challenge_name, flag, accepted, reason)
        if accepted and result.status in {"correct", "already_solved"}:
            await _record_coordinator_confirmation(deps, challenge_name, flag, reason)
        return result.display
    except Exception as e:
        return f"confirm_submission error: {e}"


async def _record_coordinator_confirmation(
    deps: CoordinatorDeps, challenge_name: str, flag: str, evidence: str
) -> None:
    """Record a coordinator-confirmed exact flag without changing submission success."""
    normalized = flag.strip()
    if not normalized:
        return
    deps.results[challenge_name] = {"flag": normalized, "submit": "platform confirmed"}
    if not deps.writeup_manager:
        return
    try:
        challenge_dir = deps.challenge_dirs.get(challenge_name)
        meta = deps.challenge_metas.get(challenge_name)
        if not challenge_dir or not meta:
            bundles = await deps.platform.list_challenges()
            bundle = next(
                (item for item in bundles if item.name == challenge_name or item.native_id == challenge_name),
                None,
            )
            if not bundle:
                raise ValueError(f"Challenge {challenge_name!r} not found")
            prepared = await deps.platform.prepare_challenge(bundle.native_id)
            challenge_dir = str(Path(deps.challenges_root) / re_slug(prepared.name))
            meta = ChallengeMeta.from_yaml(Path(challenge_dir) / "metadata.yml")
            deps.challenge_dirs[prepared.name] = challenge_dir
            deps.challenge_metas[prepared.name] = meta
        await deps.writeup_manager.record_and_schedule(
            challenge_dir,
            meta,
            normalized,
            "platform_confirmed",
            evidence=(evidence,),
        )
    except Exception:
        logger.exception("Could not queue coordinator writeup for %s", challenge_name)


async def do_kill_swarm(deps: CoordinatorDeps, challenge_name: str) -> str:
    swarm = deps.swarms.get(challenge_name)
    if not swarm:
        return f"No swarm running for {challenge_name}"
    swarm.kill()
    return f"Swarm for {challenge_name} cancelled"


async def do_bump_agent(deps: CoordinatorDeps, challenge_name: str, model_spec: str, insights: str) -> str:
    swarm = deps.swarms.get(challenge_name)
    if not swarm:
        return f"No swarm running for {challenge_name}"
    solver = swarm.solvers.get(model_spec)
    if not solver:
        return f"No solver for {model_spec} in {challenge_name}"
    solver.bump(insights)
    return f"Bumped {model_spec} on {challenge_name}"


async def do_read_solver_trace(deps: CoordinatorDeps, challenge_name: str, model_spec: str, last_n: int = 20) -> str:
    """Read the last N trace events from a solver's JSONL log."""
    swarm = deps.swarms.get(challenge_name)
    if not swarm:
        return f"No swarm for {challenge_name}"
    solver = swarm.solvers.get(model_spec)
    if not solver:
        return f"No solver for {model_spec}"
    trace_path = getattr(solver, "tracer", None)
    if not trace_path:
        return "No tracer on solver"
    path = trace_path.path if hasattr(trace_path, "path") else str(trace_path)
    try:
        lines = Path(path).read_text().strip().split("\n")
        recent = lines[-last_n:]
        summary = []
        for line in recent:
            try:
                d = json.loads(line)
                t = d.get("type", "?")
                if t == "tool_call":
                    args_str = str(d.get("args", ""))[:100]
                    summary.append(f"step {d.get('step','?')} CALL {d.get('tool','?')}: {args_str}")
                elif t == "tool_result":
                    result_str = str(d.get("result", ""))[:100]
                    summary.append(f"step {d.get('step','?')} RESULT {d.get('tool','?')}: {result_str}")
                elif t in ("finish", "error", "bump", "turn_failed"):
                    summary.append(f"** {t}: {json.dumps({k:v for k,v in d.items() if k != 'ts'})}")
                elif t == "usage":
                    summary.append(f"usage: in={d.get('input_tokens',0)} out={d.get('output_tokens',0)} cost=${d.get('cost_usd',0):.4f}")
                else:
                    summary.append(f"{t}: {str(d)[:80]}")
            except Exception:
                summary.append(line[:100])
        return "\n".join(summary)
    except FileNotFoundError:
        return f"Trace file not found: {path}"
    except Exception as e:
        return f"Error reading trace: {e}"


async def do_broadcast(deps: CoordinatorDeps, challenge_name: str, message: str) -> str:
    """Broadcast a message to all solvers working on a challenge."""
    swarm = deps.swarms.get(challenge_name)
    if not swarm:
        return f"No swarm running for {challenge_name}"
    await swarm.message_bus.broadcast(message)
    return f"Broadcast to all solvers on {challenge_name}"


def re_slug(name: str) -> str:
    """Match the platform adapters' stable challenge directory naming."""
    import re

    slug = re.sub(r'[<>:"/\\|?*\.\x00-\x1f]', "", name.lower().strip())
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-") or "challenge"


async def do_prepare_challenge(deps: CoordinatorDeps, challenge_id: str) -> str:
    candidates = await deps.platform.list_challenges()
    candidate = next(
        (challenge for challenge in candidates if challenge.native_id == challenge_id or challenge.name == challenge_id),
        None,
    )
    if candidate is None:
        return f"Challenge '{challenge_id}' not found on the configured platform"
    bundle = await deps.platform.prepare_challenge(challenge_id)
    package_state = await deps.platform.get_challenge_state(bundle.name)
    challenge_dir = Path(
        package_state.get("package_dir") or Path(deps.challenges_root) / re_slug(bundle.name)
    )
    deps.challenge_metas[bundle.name] = ChallengeMeta.from_yaml(
        challenge_dir / "metadata.yml"
    )
    deps.challenge_dirs[bundle.name] = str(challenge_dir)
    return json.dumps(bundle.model_dump(mode="json"), indent=2, ensure_ascii=False)


async def do_start_environment(deps: CoordinatorDeps, challenge_name: str) -> str:
    info = await deps.platform.start_environment(challenge_name)
    return json.dumps(info.model_dump(mode="json"), indent=2, ensure_ascii=False)


async def do_register_challenge(deps: CoordinatorDeps, data: dict) -> str:
    register = getattr(deps.platform, "register_challenge", None)
    if not register:
        return "The configured platform does not support Agent registration."
    bundle = register(data)
    return json.dumps(bundle.model_dump(mode="json"), indent=2, ensure_ascii=False)


async def do_set_environment(deps: CoordinatorDeps, challenge_name: str, data: dict) -> str:
    setter = getattr(deps.platform, "set_environment", None)
    if not setter:
        return "The configured platform does not support Agent environment registration."
    info = setter(challenge_name, data)
    return json.dumps(info.model_dump(mode="json"), indent=2, ensure_ascii=False)


async def do_import_download(deps: CoordinatorDeps, challenge_name: str, filename: str = "") -> str:
    importer = getattr(deps.platform, "import_latest_download", None)
    if not importer:
        return "The configured platform does not support browser download import."
    result = await importer(challenge_name, filename)
    return json.dumps(result, indent=2)


async def do_list_attachments(deps: CoordinatorDeps, challenge_name: str) -> str:
    getter = getattr(deps.platform, "list_attachment_candidates", None)
    if not getter:
        return "The configured platform does not support attachment candidates."
    candidates = await getter(challenge_name)
    return json.dumps([candidate.as_dict() for candidate in candidates], ensure_ascii=False, indent=2)


async def do_download_attachment(deps: CoordinatorDeps, challenge_name: str, attachment_id: str) -> str:
    downloader = getattr(deps.platform, "download_attachment", None)
    if not downloader:
        return "The configured platform does not support explicit attachment downloads."
    artifact = await downloader(challenge_name, attachment_id)
    return json.dumps(artifact.as_dict(), ensure_ascii=False, indent=2)


async def do_get_challenge_state(deps: CoordinatorDeps, challenge_name: str) -> str:
    getter = getattr(deps.platform, "get_challenge_state", None)
    if not getter:
        return "The configured platform does not expose challenge state."
    return json.dumps(await getter(challenge_name), ensure_ascii=False, indent=2, default=str)


async def do_mark_needs_input(deps: CoordinatorDeps, challenge_name: str, reason: str) -> str:
    marker = getattr(deps.platform, "mark_needs_input", None)
    if not marker:
        return "The configured platform does not support needs_input state."
    deps.pending_challenges.pop(challenge_name, None)
    deps.pending_since.pop(challenge_name, None)
    return await marker(challenge_name, reason)


async def do_retry_challenge_preparation(deps: CoordinatorDeps, challenge_name: str) -> str:
    retry = getattr(deps.platform, "retry_challenge_preparation", None)
    if not retry:
        return "The configured platform does not support preparation retry."
    deps.pending_challenges.pop(challenge_name, None)
    deps.pending_since.pop(challenge_name, None)
    return await retry(challenge_name)


async def do_save_recipe(deps: CoordinatorDeps, data: dict) -> str:
    saver = getattr(deps.platform, "save_recipe", None)
    if not saver:
        return "The configured platform does not support browser recipe storage."
    return f"Saved recipe: {saver(data)}"
