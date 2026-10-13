"""Shared coordinator event loop — used by both Claude SDK and Codex coordinators."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import traceback
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from backend.challenge_filter import normalize_challenge_types
from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.models import DEFAULT_MODELS
from backend.platforms.base import PlatformAdapter
from backend.platforms.factory import create_platform
from backend.poller import CTFdPoller
from backend.preparation import PREPARABLE_STATES, ChallengePreparationManager
from backend.prompts import ChallengeMeta
from backend.submission_setup import ensure_submission_setup
from backend.tracing import CoordinatorTracer, cancellation_origin
from backend.writeups import WriteupManager

logger = logging.getLogger(__name__)

# Callable type for a coordinator turn: (message) -> None
TurnFn = Callable[[str], Coroutine[Any, Any, None]]


def _close_trace_if_owned(deps: CoordinatorDeps) -> None:
    if deps.tracer and not getattr(deps, "defer_trace_close", False):
        deps.tracer.close()


def _cleanup_action(tracer: CoordinatorTracer | None, name: str, action) -> None:
    call_id = tracer.start_operation("cleanup", name) if tracer else None
    try:
        action()
    except BaseException as exc:
        if tracer and call_id:
            tracer.end_operation(call_id,
                                 "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                 error=exc)
        raise
    else:
        if tracer and call_id:
            tracer.end_operation(call_id, "completed")


async def _cleanup_step(tracer: CoordinatorTracer | None, name: str, awaitable) -> None:
    call_id = tracer.start_operation("cleanup", name) if tracer else None
    try:
        await awaitable
    except BaseException as exc:
        if tracer and call_id:
            tracer.end_operation(call_id,
                                 "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                 error=exc)
        raise
    else:
        if tracer and call_id:
            tracer.end_operation(call_id, "completed")


async def _guarded_step(tracer: CoordinatorTracer | None, name: str, awaitable) -> None:
    """Run one cleanup step without letting its failure skip the remaining steps."""
    try:
        await _cleanup_step(tracer, name, awaitable)
    except asyncio.CancelledError:
        logger.info("Cleanup step %s was cancelled; continuing shutdown", name)
    except Exception as exc:
        logger.warning("Cleanup step %s failed: %s", name, exc)


def _guarded_action(tracer: CoordinatorTracer | None, name: str, action) -> None:
    try:
        _cleanup_action(tracer, name, action)
    except Exception as exc:
        logger.warning("Cleanup action %s failed: %s", name, exc)


async def _run_shutdown(cleanup: Coroutine[Any, Any, None]) -> None:
    """Let the shutdown sequence finish even while this task keeps being cancelled.

    anyio re-delivers cancellation to tasks inside a cancelled scope, so awaiting the
    sequence here would abort the remaining steps. It runs in its own task, outside
    that scope, and is re-awaited after every re-delivery.
    """
    task = asyncio.create_task(cleanup, name="coordinator-shutdown")
    while True:
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            if task.done():
                return
            current = asyncio.current_task()
            if current is not None:
                current.uncancel()
        else:
            return


async def _shutdown_services(
    deps: CoordinatorDeps,
    platform: PlatformAdapter,
    cost_tracker: CostTracker,
    poller: CTFdPoller,
    preparation: ChallengePreparationManager,
    msg_server: asyncio.Server | None,
) -> None:
    tracer = deps.tracer
    if msg_server:
        _guarded_action(tracer, "message_server.close", msg_server.close)
        await _guarded_step(tracer, "message_server.wait_closed", msg_server.wait_closed())
    await _guarded_step(tracer, "preparation.stop", preparation.stop())
    await _guarded_step(tracer, "poller.stop", poller.stop())
    for name, swarm in deps.swarms.items():
        _guarded_action(tracer, f"swarm.kill:{name}", swarm.kill)
    for name, task in deps.swarm_tasks.items():
        _guarded_action(tracer, f"swarm_task.cancel:{name}", task.cancel)
    if deps.swarm_tasks:
        await _guarded_step(tracer, "swarm_tasks.gather",
                            asyncio.gather(*deps.swarm_tasks.values(), return_exceptions=True))
    if deps.analysis_gateway:
        await _guarded_step(tracer, "analysis_gateway.close", deps.analysis_gateway.close())
    if deps.writeup_manager:
        await _guarded_step(tracer, "writeup_manager.wait_for_pending",
                            deps.writeup_manager.wait_for_pending(timeout=5))
    _guarded_action(tracer, "cost_tracker.log_summary", cost_tracker.log_summary)
    await _guarded_step(tracer, "platform.close", platform.close())
    if tracer:
        tracer.event("coordinator_stopped")


def build_deps(
    settings: Settings,
    model_specs: list[str] | None = None,
    challenges_root: str = "challenges",
    no_submit: bool = False,
    challenge_dirs: dict[str, str] | None = None,
    challenge_metas: dict[str, ChallengeMeta] | None = None,
) -> tuple[PlatformAdapter, CostTracker, CoordinatorDeps]:
    """Create the configured platform, cost tracker, and coordinator deps."""
    platform = create_platform(settings, challenges_root, allow_submit=not no_submit)
    cost_tracker = CostTracker()
    specs = model_specs or list(DEFAULT_MODELS)
    Path(challenges_root).mkdir(parents=True, exist_ok=True)

    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=cost_tracker,
        settings=settings,
        model_specs=specs,
        challenges_root=challenges_root,
        no_submit=no_submit,
        max_concurrent_challenges=getattr(settings, "max_concurrent_challenges", 10),
        challenge_types=normalize_challenge_types(getattr(settings, "challenge_types", [])),
        challenge_dirs=challenge_dirs or {},
        challenge_metas=challenge_metas or {},
        tracer=CoordinatorTracer(getattr(settings, "challenge_run_id", ""),
                                 stamp=getattr(settings, "run_log_stamp", "")),
        writeup_manager=WriteupManager(
            settings,
            default_model_spec=getattr(settings, "writeup_model_spec", "") or specs[0],
        ),
    )
    if hasattr(platform, "browser"):
        platform.browser.tracer = deps.tracer

    return platform, cost_tracker, deps


async def run_event_loop(
    deps: CoordinatorDeps,
    platform: PlatformAdapter,
    cost_tracker: CostTracker,
    turn_fn: TurnFn,
    status_interval: int = 60,
) -> dict[str, Any]:
    """Run the shared coordinator event loop.

    Args:
        deps: Coordinator dependencies (shared state).
        platform adapter (for poller).
        cost_tracker: Cost tracker.
        turn_fn: Async function that sends a message to the coordinator LLM.
        status_interval: Seconds between status updates.
    """
    # The Coordinator already has browser tools, but no poller, preparation
    # queue, or solver may run until submit-enabled platforms are ready.
    try:
        setup_issue = await ensure_submission_setup(deps, turn_fn)
    except BaseException as exc:
        if deps.tracer:
            deps.tracer.event("startup_failed", stage="submission_setup",
                              error_type=type(exc).__name__, error=str(exc),
                              traceback="".join(traceback.format_exception(exc)),
                              **(cancellation_origin() if isinstance(exc, asyncio.CancelledError) else {}))
        await _cleanup_step(deps.tracer, "platform.close", platform.close())
        if deps.tracer:
            _close_trace_if_owned(deps)
        raise
    if setup_issue:
        error = f"Submission setup failed: {setup_issue}. Use --no-submit for verification-only solving."
        logger.error(error)
        await _cleanup_step(deps.tracer, "platform.close", platform.close())
        if deps.tracer:
            deps.tracer.event("submission_setup_failed", reason=setup_issue)
            _close_trace_if_owned(deps)
        return {"results": deps.results, "total_cost_usd": cost_tracker.total_cost_usd,
                "total_tokens": cost_tracker.total_tokens, "error": error}

    poller = CTFdPoller(platform=platform, interval_s=5.0)
    preparation = ChallengePreparationManager(
        platform,
        concurrency=int(getattr(deps.settings, "preparation_concurrency", 4) or 4),
    )
    msg_server: asyncio.Server | None = None
    try:
        if getattr(deps.settings, "solver_mcp_config", ""):
            from backend.solver_mcp import SolverMcpGateway

            deps.analysis_gateway = SolverMcpGateway(deps.settings.solver_mcp_config)
            await deps.analysis_gateway.start()
        await poller.start()
        await preparation.start()
        await preparation.pause_and_wait()
        if deps.writeup_manager:
            await deps.writeup_manager.resume_pending(deps.challenges_root)
        msg_server = await _start_msg_server(deps.operator_inbox, deps.msg_port)
    except BaseException as exc:
        if deps.tracer:
            deps.tracer.event("startup_failed", stage="services",
                              error_type=type(exc).__name__, error=str(exc),
                              traceback="".join(traceback.format_exception(exc)),
                              **(cancellation_origin() if isinstance(exc, asyncio.CancelledError) else {}))
        await _cleanup_step(deps.tracer, "preparation.stop", preparation.stop())
        await _cleanup_step(deps.tracer, "poller.stop", poller.stop())
        if deps.analysis_gateway:
            await _cleanup_step(deps.tracer, "analysis_gateway.close", deps.analysis_gateway.close())
        await _cleanup_step(deps.tracer, "platform.close", platform.close())
        if deps.tracer:
            _close_trace_if_owned(deps)
        raise

    logger.info(
        "Coordinator starting: %d models, %d challenges, %d solved",
        len(deps.model_specs),
        len(poller.known_challenges),
        len(poller.known_solved),
    )

    unsolved = poller.known_challenges - poller.known_solved
    target_instruction = (
        "The operator requested a challenge-type preference: "
        f"{sorted(deps.challenge_types)}. This is a soft preference, not a hard category filter. "
        "Inspect each challenge's category, name, description, tags, files, and connection info "
        "before deciding whether it matches. Do not spawn a swarm until you have classified it."
        if deps.challenge_types
        else "No challenge-type preference was provided."
    )
    initial_msg = (
        f"CTF is LIVE. {len(poller.known_challenges)} challenges, "
        f"{len(poller.known_solved)} solved.\n"
        f"Unsolved: {sorted(unsolved) if unsolved else 'NONE'}\n"
        f"{target_instruction}\n"
        "Inspect and register each selected challenge, mark environment_required when the page "
        "has an environment control, start/register required environments, and spawn only after "
        "get_challenge_state reports ready."
    )

    fatal_error: str | None = None
    try:
        try:
            await turn_fn(initial_msg)
        finally:
            preparation.resume()

        # With a type preference, the Coordinator must classify challenges first.
        if not deps.challenge_types:
            await _queue_or_spawn_unsolved(deps, poller, preparation)

        last_status = asyncio.get_event_loop().time()

        while True:
            events = []
            evt = await poller.get_event(timeout=5.0)
            if evt:
                events.append(evt)
            events.extend(poller.drain_events())

            # Auto-kill swarms for solved challenges
            for evt in events:
                if evt.kind == "challenge_solved" and evt.challenge_name in deps.swarms:
                    swarm = deps.swarms[evt.challenge_name]
                    if not swarm.cancel_event.is_set():
                        swarm.kill()
                        logger.info("Auto-killed swarm for: %s", evt.challenge_name)
                if evt.kind == "challenge_solved":
                    deps.deferred_auto_spawn.discard(evt.challenge_name)
                    confirmed_flag_getter = getattr(deps.platform, "get_confirmed_flag", None)
                    confirmed_flag = (
                        confirmed_flag_getter(evt.challenge_name)
                        if callable(confirmed_flag_getter)
                        else None
                    )
                    if confirmed_flag:
                        from backend.agents.coordinator_core import _record_coordinator_confirmation

                        await _record_coordinator_confirmation(
                            deps,
                            evt.challenge_name,
                            confirmed_flag,
                            "Exact browser submission confirmation",
                        )
                    marker = getattr(deps.platform, "mark_challenge_solved", None)
                    if marker:
                        try:
                            await marker(evt.challenge_name)
                        except Exception as exc:
                            logger.warning("Could not persist solved state for %s: %s", evt.challenge_name, exc)

            parts: list[str] = []
            for evt in events:
                if evt.kind == "new_challenge":
                    if deps.challenge_types:
                        parts.append(
                            f"NEW CHALLENGE: '{evt.challenge_name}' appeared. Classify it against the requested preference before spawning."
                        )
                    elif preparation.supported:
                        queued = await preparation.enqueue(evt.challenge_name)
                        action = "queued for preparation" if queued else "already queued or preparing"
                        parts.append(
                            f"NEW CHALLENGE: '{evt.challenge_name}' appeared; {action}. "
                            "Do not spawn until the package is ready."
                        )
                    else:
                        parts.append(f"NEW CHALLENGE: '{evt.challenge_name}' appeared. Spawn a swarm.")
                        await _auto_spawn_one(deps, evt.challenge_name)
                elif evt.kind == "challenge_solved":
                    parts.append(f"SOLVED: '{evt.challenge_name}' — swarm auto-killed.")

            # Detect finished swarms
            for name, task in list(deps.swarm_tasks.items()):
                if task.done() and name not in deps.reported_finished_swarms:
                    parts.append(f"SOLVER FINISHED: Swarm for '{name}' completed. Check results or retry.")
                    deps.reported_finished_swarms.add(name)

            # Drain solver-to-coordinator messages
            while True:
                try:
                    solver_msg = deps.coordinator_inbox.get_nowait()
                    parts.append(f"SOLVER MESSAGE: {solver_msg}")
                except asyncio.QueueEmpty:
                    break

            for prep_event in preparation.drain_events():
                details = (
                    f" details={json.dumps(prep_event.details, ensure_ascii=False, sort_keys=True)}"
                    if prep_event.details
                    else ""
                )
                if prep_event.state == "ready":
                    if deps.challenge_types:
                        parts.append(
                            f"PREPARATION READY: '{prep_event.challenge_name}'. {prep_event.message}.{details} "
                            "Classify it against the requested challenge-type preference before spawning."
                        )
                    else:
                        result = await _auto_spawn_one(deps, prep_event.challenge_name)
                        parts.append(
                            f"PREPARATION READY: '{prep_event.challenge_name}'. {prep_event.message}.{details} {result}"
                        )
                elif prep_event.state == "waiting_for_environment":
                    deps.pending_challenges.setdefault(
                        prep_event.challenge_name, prep_event.message
                    )
                    deps.pending_since.setdefault(
                        prep_event.challenge_name, time.monotonic()
                    )
                    parts.append(
                        f"WAITING FOR ENVIRONMENT: '{prep_event.challenge_name}': {prep_event.message}.{details} "
                        "Start the local Compose environment with start_environment, or inspect the "
                        "platform page and register a remote environment with set_environment."
                    )
                elif prep_event.state == "needs_input":
                    deps.pending_challenges.setdefault(
                        prep_event.challenge_name, prep_event.message
                    )
                    deps.pending_since.setdefault(
                        prep_event.challenge_name, time.monotonic()
                    )
                    parts.append(
                        f"PREPARATION NEEDS INPUT: '{prep_event.challenge_name}': {prep_event.message}.{details}"
                    )

            for pending_name in list(deps.pending_challenges):
                if pending_name not in deps.swarms:
                    try:
                        package_state = await deps.platform.get_challenge_state(pending_name)
                    except Exception:
                        package_state = {}
                    package_state_name = package_state.get("state")
                    if package_state_name in PREPARABLE_STATES:
                        await preparation.enqueue(pending_name)
                        continue
                    if package_state_name == "waiting_for_environment":
                        started = deps.pending_since.get(pending_name, time.monotonic())
                        timeout = int(deps.settings.coordinator_decision_timeout_seconds)
                        if timeout <= 0 or time.monotonic() - started < timeout:
                            continue
                        from backend.agents.coordinator_core import do_mark_needs_input

                        reason = "Coordinator decision timeout while starting challenge environment"
                        parts.append(await do_mark_needs_input(deps, pending_name, reason))
                        continue
                    if package_state_name == "needs_input":
                        continue
                    if deps.challenge_types and pending_name not in deps.selected_challenges:
                        if package_state_name == "ready":
                            deps.pending_challenges.pop(pending_name, None)
                            deps.pending_since.pop(pending_name, None)
                            parts.append(
                                f"PACKAGE READY: '{pending_name}'. Classify it against the requested "
                                "challenge-type preference before spawning."
                            )
                        continue
                    started = deps.pending_since.get(pending_name, time.monotonic())
                    timeout = int(deps.settings.coordinator_decision_timeout_seconds)
                    if timeout > 0 and time.monotonic() - started >= timeout:
                        from backend.agents.coordinator_core import do_mark_needs_input
                        reason = "Coordinator decision timeout while preparing challenge package"
                        parts.append(await do_mark_needs_input(deps, pending_name, reason))
                        continue
                    result = await _auto_spawn_one(deps, pending_name)
                    if result and result.startswith("Swarm spawned"):
                        parts.append(result)

            parts.extend(await _drain_deferred_auto_spawns(deps, poller.known_solved))

            # Drain operator messages
            while True:
                try:
                    op_msg = deps.operator_inbox.get_nowait()
                    parts.append(f"OPERATOR MESSAGE: {op_msg}")
                    logger.info("Operator message: %s", op_msg[:200])
                except asyncio.QueueEmpty:
                    break

            # Periodic status update — only when there are active swarms or other events
            now = asyncio.get_event_loop().time()
            if now - last_status >= status_interval:
                last_status = now
                active = [n for n, t in deps.swarm_tasks.items() if not t.done()]
                solved_set = poller.known_solved
                unsolved_set = poller.known_challenges - solved_set
                preparation_states = await preparation.state_counts()
                status_line = (
                    f"STATUS: {len(solved_set)} solved, {len(unsolved_set)} unsolved, "
                    f"{len(active)} active swarms, {preparation.active_count} preparing, "
                    f"{preparation.queued_count} queued, package_states={preparation_states}. "
                    f"Cost: ${cost_tracker.total_cost_usd:.2f}"
                )
                # Only send to coordinator if there's something happening
                if active or parts:
                    parts.append(status_line)
                else:
                    logger.info(f"Event -> coordinator: {status_line}")

            if parts:
                msg = "\n\n".join(parts)
                logger.info("Event -> coordinator: %s", msg[:200])
                await preparation.pause_and_wait()
                try:
                    await turn_fn(msg)
                finally:
                    preparation.resume()

    except (KeyboardInterrupt, asyncio.CancelledError) as exc:
        logger.info("Coordinator shutting down...")
        if deps.tracer:
            deps.tracer.event("coordinator_cancelled", **cancellation_origin(),
                              error_type=type(exc).__name__,
                              traceback="".join(traceback.format_exception(exc)),
                              pending=deps.tracer.pending_operations())
    except Exception as e:
        logger.error("Coordinator fatal: %s", e, exc_info=True)
        if deps.tracer:
            deps.tracer.event("coordinator_fatal", error_type=type(e).__name__,
                              error=str(e), traceback="".join(traceback.format_exception(e)))
        fatal_error = f"Coordinator fatal: {e}"
    finally:
        try:
            await _run_shutdown(
                _shutdown_services(deps, platform, cost_tracker, poller, preparation, msg_server)
            )
        finally:
            if deps.tracer:
                deps.tracer.event("shutdown_trace_closed", pending=deps.tracer.pending_operations())
                _close_trace_if_owned(deps)

    return {
        "results": deps.results,
        "total_cost_usd": cost_tracker.total_cost_usd,
        "total_tokens": cost_tracker.total_tokens,
        **({"error": fatal_error} if fatal_error else {}),
    }


async def _auto_spawn_one(deps: CoordinatorDeps, challenge_name: str) -> str:
    """Auto-spawn a swarm for a single challenge if not already running."""
    if challenge_name in deps.swarms:
        task = deps.swarm_tasks.get(challenge_name)
        return (
            f"Swarm already finished for {challenge_name}"
            if task and task.done()
            else f"Swarm still running for {challenge_name}"
        )
    active = sum(1 for t in deps.swarm_tasks.values() if not t.done())
    if active >= deps.max_concurrent_challenges:
        deps.deferred_auto_spawn.add(challenge_name)
        return f"At capacity for {challenge_name}"
    try:
        from backend.agents.coordinator_core import do_spawn_swarm
        result = await do_spawn_swarm(deps, challenge_name)
        if result.startswith("Swarm spawned"):
            deps.deferred_auto_spawn.discard(challenge_name)
        logger.info(f"Auto-spawn {challenge_name}: {result[:100]}")
        return result
    except Exception as e:
        logger.warning(f"Auto-spawn failed for {challenge_name}: {e}")
        return f"Auto-spawn failed for {challenge_name}: {e}"


async def _drain_deferred_auto_spawns(
    deps: CoordinatorDeps, solved: set[str]
) -> list[str]:
    messages: list[str] = []
    for name in sorted(deps.deferred_auto_spawn):
        if name in solved:
            deps.deferred_auto_spawn.discard(name)
            continue
        result = await _auto_spawn_one(deps, name)
        if result.startswith("At capacity"):
            break
        if result.startswith("Swarm spawned"):
            messages.append(result)
        else:
            deps.deferred_auto_spawn.discard(name)
    return messages


async def _queue_or_spawn_unsolved(deps: CoordinatorDeps, poller, preparation) -> None:
    """Queue package preparation before spawning browser-platform swarms."""
    unsolved = poller.known_challenges - poller.known_solved
    for name in sorted(unsolved):
        if preparation.supported:
            queued = await preparation.enqueue(name)
            if queued:
                logger.info("Challenge queued for preparation: %s", name)
        else:
            await _auto_spawn_one(deps, name)


async def _start_msg_server(inbox: asyncio.Queue, port: int = 0) -> asyncio.Server | None:
    """Start a tiny HTTP server that accepts operator messages via POST."""

    async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # Read HTTP request
            request_line = await asyncio.wait_for(reader.readline(), timeout=5)
            headers: dict[str, str] = {}
            while True:
                line = await asyncio.wait_for(reader.readline(), timeout=5)
                if line in (b"\r\n", b"\n", b""):
                    break
                if b":" in line:
                    k, v = line.decode().split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            method = request_line.decode().split()[0] if request_line else ""
            content_length = int(headers.get("content-length", 0))

            if method == "POST" and content_length > 0:
                body = await asyncio.wait_for(reader.read(content_length), timeout=5)
                try:
                    data = json.loads(body)
                    message = data.get("message", body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    message = body.decode("utf-8", errors="replace")

                inbox.put_nowait(message)
                resp = json.dumps({"ok": True, "queued": message[:200]})
                writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(resp)}\r\n\r\n{resp}".encode())
            else:
                resp = json.dumps({"error": "POST with JSON body required", "usage": "POST {\"message\": \"...\"}"})
                writer.write(f"HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nContent-Length: {len(resp)}\r\n\r\n{resp}".encode())

            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    try:
        server = await asyncio.start_server(_handle, "127.0.0.1", port)
        actual_port = server.sockets[0].getsockname()[1]
        logger.info(f"Operator message endpoint listening on http://127.0.0.1:{actual_port}")
        return server
    except OSError as e:
        logger.warning(f"Could not start operator message endpoint: {e}")
        return None
