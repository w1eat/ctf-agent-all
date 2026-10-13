"""Codex coordinator — drives `codex app-server` via JSON-RPC for coordination."""

from __future__ import annotations

import asyncio
import itertools
import json
import logging
from typing import Any

from backend.agents.coordinator_core import (
    do_broadcast,
    do_bump_agent,
    do_check_swarm_status,
    do_confirm_submission,
    do_coordinator_shell,
    do_download_attachment,
    do_fetch_challenges,
    do_get_challenge_state,
    do_get_solve_status,
    do_import_download,
    do_kill_swarm,
    do_list_attachments,
    do_mark_needs_input,
    do_prepare_challenge,
    do_read_solver_trace,
    do_register_challenge,
    do_retry_challenge_preparation,
    do_save_recipe,
    do_set_environment,
    do_spawn_swarm,
    do_start_environment,
    do_submit_flag,
)
from backend.agents.coordinator_loop import _cleanup_step, build_deps, run_event_loop
from backend.config import Settings
from backend.deps import CoordinatorDeps
from backend.platforms.base import BrowserToolProvider
from backend.platforms.recipes import SAVE_RECIPE_TOOL_SCHEMA
from backend.submission_setup import CoordinatorTurnError

logger = logging.getLogger(__name__)

_rpc_counter = itertools.count(1)

COORDINATOR_PROMPT = """\
You are a CTF competition coordinator running for the ENTIRE duration of a live competition.
Your job is to maximize the number of challenges solved while minimizing cost.

Strategy:
- Spawn swarms for unsolved challenges, prioritizing by solve count (easy first), while respecting configured concurrency and budgets
- Use read_solver_trace to monitor what each solver is doing and where it's stuck
- When agents are stuck, read their traces, then craft targeted bumps with specific technical guidance
- Use broadcast to share cross-solver insights (e.g. flag format discovery, shared vulnerabilities)

CRITICAL RULES:
- Do not kill a healthy swarm. A swarm may finish on a verified flag, an explicit
  budget/timeout state, or a platform/operator stop request.
- When a solver seems stuck, bump it with very specific technical guidance based on
  its trace. Tell it exactly what to try next — specific tools, techniques, approaches.
- Treat candidate flags as unverified until the swarm reports an independent verifier.
- In submit mode, complete the mandatory browser submission-recipe setup turn first.
  Inspect an unsolved challenge's real flag form and its submit interaction (button
  click or Enter) and call save_recipe. Recipe targets are plain string selectors,
  such as `textarea[aria-label="Flag"]`; do not pass role/name objects or ephemeral
  snapshot refs. Never invent targets or submit a test flag.
  Swarm spawning is blocked by code until the recipe is ready.
- Respect the reported time, step, concurrency, and cost budgets.

When the platform is unknown, use the Playwright browser tools to discover it. Always snapshot
before interacting with page elements. For every challenge, register a normalized record:
set `environment_required=true` when the page has a challenge-environment section or a
start-environment control, register only real attachment objects, include `challenge_url`
and visible attachment target/page metadata, and never treat snapshots or logs as files.
If an environment is required, start it in the browser, observe the resulting URL, host, or
port, and call `set_environment`; a visible button alone is not a ready environment.
Package preparation and downloads are automatic. Do not call `spawn_swarm` until
`get_challenge_state` reports `ready`; the program enforces this gate. Use attachment tools
for diagnostics or recovery, handle `waiting_for_environment` by starting/registering the
environment, repair `needs_input` metadata, and use retry_challenge_preparation for
transient failures. Manage the browser with `browser_status`, `browser_start`,
`browser_restart`, and `browser_close`. If any browser tool reports `Connection closed`,
restart the browser transport and take a fresh snapshot before retrying. Save only
credential-free recipes. Never expose browser credentials.

Challenge-type selection is a soft preference, not a fixed category filter. Inspect category,
name, description, tags, files, connection information, and environment behavior. Do not equate
generic labels such as `binary` or `exploit` with PWN automatically. When a preference is present,
classify candidates yourself and call spawn_swarm only for matching challenges.

You will receive event messages. Respond with tool calls to manage the competition.
"""

COORDINATOR_TOOLS = [
    {
        "name": "fetch_challenges",
        "description": "List all challenges with category, points, solve count, and status.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_solve_status",
        "description": "Check which challenges are solved and which swarms are running.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "spawn_swarm",
        "description": "Launch all solver models on a challenge.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_name": {"type": "string"}},
            "required": ["challenge_name"],
        },
    },
    {
        "name": "check_swarm_status",
        "description": "Get per-agent progress for a swarm.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_name": {"type": "string"}},
            "required": ["challenge_name"],
        },
    },
    {
        "name": "submit_flag",
        "description": "Submit a flag through the configured platform.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_name": {"type": "string"}, "flag": {"type": "string"}},
            "required": ["challenge_name", "flag"],
        },
    },
    {
        "name": "kill_swarm",
        "description": "Cancel all agents for a challenge.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_name": {"type": "string"}},
            "required": ["challenge_name"],
        },
    },
    {
        "name": "bump_agent",
        "description": "Send targeted insights to a stuck agent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "challenge_name": {"type": "string"},
                "model_spec": {"type": "string"},
                "insights": {"type": "string"},
            },
            "required": ["challenge_name", "model_spec", "insights"],
        },
    },
    {
        "name": "broadcast",
        "description": "Broadcast a strategic hint to ALL solvers on a challenge.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_name": {"type": "string"}, "message": {"type": "string"}},
            "required": ["challenge_name", "message"],
        },
    },
    {
        "name": "read_solver_trace",
        "description": "Read recent trace events from a specific solver.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "challenge_name": {"type": "string"},
                "model_spec": {"type": "string"},
                "last_n": {"type": "integer", "default": 20},
            },
            "required": ["challenge_name", "model_spec"],
        },
    },
    {
        "name": "confirm_submission",
        "description": "Judge browser evidence from submit_flag and confirm only a clearly accepted exact flag.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}, "flag": {"type": "string"}, "accepted": {"type": "boolean"}, "reason": {"type": "string"}}, "required": ["challenge_name", "flag", "accepted", "reason"]},
    },
    {
        "name": "prepare_challenge",
        "description": "Prepare a discovered challenge package for solver agents.",
        "inputSchema": {"type": "object", "properties": {"challenge_id": {"type": "string"}}, "required": ["challenge_id"]},
    },
    {
        "name": "start_environment",
        "description": "Start or retrieve a challenge environment.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}}, "required": ["challenge_name"]},
    },
    {
        "name": "register_challenge",
        "description": "Register a normalized challenge discovered through the browser.",
        "inputSchema": {"type": "object", "properties": {"data": {"type": "object"}}, "required": ["data"]},
    },
    {
        "name": "set_environment",
        "description": "Attach a discovered environment to a challenge.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}, "data": {"type": "object"}}, "required": ["challenge_name", "data"]},
    },
    {
        "name": "list_attachments",
        "description": "List registered attachment candidates for a challenge.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}}, "required": ["challenge_name"]},
    },
    {
        "name": "download_attachment",
        "description": "Download one explicitly selected attachment and verify it.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}, "attachment_id": {"type": "string"}}, "required": ["challenge_name", "attachment_id"]},
    },
    {
        "name": "get_challenge_state",
        "description": "Get persistent package readiness and attachment state.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}}, "required": ["challenge_name"]},
    },
    {
        "name": "mark_challenge_needs_input",
        "description": "Mark a challenge blocked when the platform needs operator input.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}, "reason": {"type": "string"}}, "required": ["challenge_name", "reason"]},
    },
    {
        "name": "retry_challenge_preparation",
        "description": "Reset a blocked challenge package so preparation can be retried.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}}, "required": ["challenge_name"]},
    },
    {
        "name": "import_latest_download",
        "description": "Import the latest Playwright download into challenge distfiles.",
        "inputSchema": {"type": "object", "properties": {"challenge_name": {"type": "string"}, "filename": {"type": "string"}}, "required": ["challenge_name"]},
    },
    {
        "name": "save_recipe",
        "description": "Save a credential-free browser submission workflow. Use steps [{action:'navigate', value:'https://host/challenges/{challenge_id}'}, {action:'type', target:'textarea[aria-label=\"Flag\"]', value:'{flag}', data:{submit:true}}] when Enter submits. Use observed selectors and never submit a test flag.",
        "inputSchema": SAVE_RECIPE_TOOL_SCHEMA,
    },
    {
        "name": "browser_status",
        "description": "Return browser MCP lifecycle status without credentials.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "browser_start",
        "description": "Start the browser MCP transport if it is stopped.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "browser_restart",
        "description": "Restart the browser MCP transport after a connection failure.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "browser_close",
        "description": "Close the browser MCP transport after platform work is complete.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

COORDINATOR_SHELL_TOOL = {
    "name": "coordinator_shell",
    "description": "Run an unrestricted host shell command and return stdout, stderr, and exit code.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "cwd": {"type": "string"},
            "timeout_seconds": {"type": "number", "default": 120},
        },
        "required": ["command"],
    },
}


class CodexCoordinator:
    """Coordinator using Codex App Server JSON-RPC."""

    def __init__(self, deps: CoordinatorDeps, model: str = "gpt-5.4") -> None:
        self.deps = deps
        self.model = model
        self._proc: asyncio.subprocess.Process | None = None
        self._thread_id: str | None = None
        self._pending_responses: dict[int, asyncio.Future] = {}
        self._reader_task: asyncio.Task | None = None
        self._turn_done: asyncio.Event = asyncio.Event()
        self._turn_error: str | None = None
        self._turn_timeout_seconds = int(deps.settings.coordinator_decision_timeout_seconds)

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            "codex", "app-server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        self._reader_task = asyncio.create_task(self._read_loop())

        await self._rpc("initialize", {
            "clientInfo": {"name": "ctf-coordinator", "version": "2.0.0"},
            "capabilities": {"experimentalApi": True},
        })
        await self._send_notification("initialized", {})

        full_access = bool(getattr(self.deps.settings, "coordinator_full_access", False))
        dynamic_tools = list(COORDINATOR_TOOLS)
        if full_access:
            dynamic_tools.append(COORDINATOR_SHELL_TOOL)

        resp = await self._rpc("thread/start", {
            "model": self.model,
            "personality": "pragmatic",
            "baseInstructions": COORDINATOR_PROMPT,
            "cwd": ".",
            "approvalPolicy": "never" if full_access else "on-request",
            "sandbox": "danger-full-access" if full_access else "read-only",
            "dynamicTools": dynamic_tools + (
                self.deps.platform.browser_tool_specs()
                if isinstance(self.deps.platform, BrowserToolProvider) else []
            ),
        })
        self._thread_id = resp.get("result", {}).get("thread", {}).get("id", "")
        if self.deps.tracer:
            self.deps.tracer.event(
                "coordinator_started",
                backend="codex",
                model=self.model,
                thread_id=self._thread_id,
                full_access=full_access,
            )
        logger.info(f"Codex coordinator started (thread={self._thread_id}, model={self.model})")

    async def turn(self, message: str) -> None:
        """Send a message and wait for the model to finish its turn."""
        if not self._proc or not self._thread_id:
            await self.start()

        self._turn_done.clear()
        self._turn_error = None
        if self.deps.tracer:
            self.deps.tracer.turn_input(message)
            turn_call_id = self.deps.tracer.start_operation("turn", "codex", message,
                                                            session_state="connected" if self._proc else "stopped")
        else:
            turn_call_id = None

        try:
            await self._rpc("turn/start", {
                "threadId": self._thread_id,
                "input": [{"type": "text", "text": message}],
            })
        except BaseException as exc:
            if self.deps.tracer and turn_call_id:
                self.deps.tracer.end_operation(turn_call_id,
                                               "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                               error=exc)
            raise

        try:
            await asyncio.wait_for(
                self._turn_done.wait(),
                timeout=self._turn_timeout_seconds if self._turn_timeout_seconds > 0 else None,
            )
        except TimeoutError:
            logger.warning("Codex coordinator turn timed out")
            # There is no portable interrupt method across app-server
            # versions. Terminate this transport so the next event starts a
            # fresh thread instead of overlapping turns on a stale session.
            await self.stop()
            if self.deps.tracer:
                self.deps.tracer.event("turn_timeout", timeout_seconds=self._turn_timeout_seconds)
                self.deps.tracer.end_operation(turn_call_id, "timeout")
            raise CoordinatorTurnError(
                f"Coordinator turn timed out after {self._turn_timeout_seconds}s"
            ) from None
        except BaseException as exc:
            if self.deps.tracer and turn_call_id:
                self.deps.tracer.end_operation(turn_call_id,
                                               "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                               error=exc)
            raise

        turn_error = self._current_turn_error()
        if turn_error:
            logger.warning(f"Codex coordinator turn error: {turn_error}")
            if self.deps.tracer:
                self.deps.tracer.event("turn_error", error=turn_error)
                self.deps.tracer.end_operation(turn_call_id, "error", output=turn_error)
            raise CoordinatorTurnError(f"Coordinator model error: {turn_error}")
        if self.deps.tracer and turn_call_id:
            self.deps.tracer.end_operation(turn_call_id, "completed")

    def _current_turn_error(self) -> str | None:
        """Read state updated asynchronously by the app-server reader task."""
        return self._turn_error

    async def stop(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
        if self._proc:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except Exception:
                self._proc.kill()
            self._proc = None

    # --- JSON-RPC transport ---

    async def _rpc(self, method: str, params: dict | None = None) -> dict:
        assert self._proc and self._proc.stdin
        msg_id = next(_rpc_counter)
        msg: dict[str, Any] = {"id": msg_id, "method": method}
        if params:
            msg["params"] = params

        future: asyncio.Future[dict] = asyncio.get_event_loop().create_future()
        self._pending_responses[msg_id] = future

        self._proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self._proc.stdin.drain()
        try:
            return await asyncio.wait_for(future, timeout=300)
        finally:
            self._pending_responses.pop(msg_id, None)

    async def _respond_to_request(self, request_id: int, result: Any) -> None:
        assert self._proc and self._proc.stdin
        resp = {"id": request_id, "result": result}
        self._proc.stdin.write((json.dumps(resp) + "\n").encode())
        await self._proc.stdin.drain()

    async def _send_notification(self, method: str, params: dict | None = None) -> None:
        assert self._proc and self._proc.stdin
        msg: dict[str, Any] = {"method": method}
        if params:
            msg["params"] = params
        self._proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self._proc.stdin.drain()

    async def _read_loop(self) -> None:
        assert self._proc and self._proc.stdout
        while True:
            line = await self._proc.stdout.readline()
            if not line:
                self._turn_done.set()
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_id = msg.get("id")

            # RPC response
            if msg_id is not None and ("result" in msg or "error" in msg):
                future = self._pending_responses.pop(msg_id, None)
                if future and not future.done():
                    if "error" in msg:
                        future.set_exception(RuntimeError(f"Codex RPC error: {msg['error']}"))
                    else:
                        future.set_result(msg)
                continue

            method = msg.get("method", "")
            params = msg.get("params", {})

            if self.deps.tracer and (method.startswith("item/") or method == "turn/completed"):
                self.deps.tracer.event("codex_event", method=method, params=params)

            # Dynamic tool call
            if method == "item/tool/call" and msg_id is not None:
                await self._handle_tool_call(msg_id, params)

            # Turn completed
            elif method == "turn/completed":
                turn = params.get("turn", {})
                if turn.get("status") == "failed":
                    self._turn_error = str(turn.get("error", "unknown"))
                self._turn_done.set()

    async def _handle_tool_call(self, request_id: int, params: dict) -> None:
        tool_name = params.get("tool", "")
        try:
            args = params.get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args)
        except Exception:
            args = {}

        logger.debug(f"Coordinator tool call: {tool_name}({args})")
        if self.deps.tracer:
            call_id = self.deps.tracer.tool_call(tool_name, args, call_id=str(request_id))
        else:
            call_id = None

        try:
            result = await self._dispatch_tool(tool_name, args)
        except asyncio.CancelledError as exc:
            if self.deps.tracer and call_id:
                self.deps.tracer.end_operation(call_id, "cancelled", error=exc)
            raise
        except Exception as e:
            result = f"Error: {e}"
            if self.deps.tracer and call_id:
                self.deps.tracer.end_operation(call_id, "error", output=result, error=e)
                call_id = None

        if self.deps.tracer and call_id:
            self.deps.tracer.tool_result(tool_name, result, call_id=call_id)

        await self._respond_to_request(request_id, {
            "contentItems": [{"type": "inputText", "text": str(result)}],
            "success": True,
        })

    async def _dispatch_tool(self, name: str, args: dict) -> str:
        deps = self.deps
        if name == "fetch_challenges":
            return await do_fetch_challenges(deps)
        elif name == "get_solve_status":
            return await do_get_solve_status(deps)
        elif name == "spawn_swarm":
            return await do_spawn_swarm(deps, args["challenge_name"])
        elif name == "check_swarm_status":
            return await do_check_swarm_status(deps, args["challenge_name"])
        elif name == "submit_flag":
            return await do_submit_flag(deps, args["challenge_name"], args["flag"])
        elif name == "confirm_submission":
            return await do_confirm_submission(deps, args["challenge_name"], args["flag"], args["accepted"], args["reason"])
        elif name == "kill_swarm":
            return await do_kill_swarm(deps, args["challenge_name"])
        elif name == "bump_agent":
            return await do_bump_agent(deps, args["challenge_name"], args["model_spec"], args["insights"])
        elif name == "broadcast":
            return await do_broadcast(deps, args["challenge_name"], args["message"])
        elif name == "read_solver_trace":
            return await do_read_solver_trace(deps, args["challenge_name"], args["model_spec"], args.get("last_n", 20))
        elif name == "prepare_challenge":
            return await do_prepare_challenge(deps, args["challenge_id"])
        elif name == "start_environment":
            return await do_start_environment(deps, args["challenge_name"])
        elif name == "register_challenge":
            return await do_register_challenge(deps, args["data"])
        elif name == "set_environment":
            return await do_set_environment(deps, args["challenge_name"], args["data"])
        elif name == "list_attachments":
            return await do_list_attachments(deps, args["challenge_name"])
        elif name == "download_attachment":
            return await do_download_attachment(deps, args["challenge_name"], args["attachment_id"])
        elif name == "get_challenge_state":
            return await do_get_challenge_state(deps, args["challenge_name"])
        elif name == "mark_challenge_needs_input":
            return await do_mark_needs_input(deps, args["challenge_name"], args["reason"])
        elif name == "retry_challenge_preparation":
            return await do_retry_challenge_preparation(deps, args["challenge_name"])
        elif name == "import_latest_download":
            return await do_import_download(deps, args["challenge_name"], args.get("filename", ""))
        elif name == "save_recipe":
            return await do_save_recipe(deps, args["data"])
        elif name == "coordinator_shell":
            return await do_coordinator_shell(
                deps,
                args.get("command", ""),
                args.get("cwd", ""),
                args.get("timeout_seconds", 120),
            )
        elif name == "browser_status":
            getter = getattr(deps.platform, "browser_status", None)
            return json.dumps(await getter() if getter else {"supported": False}, ensure_ascii=False)
        elif name == "browser_start":
            starter = getattr(deps.platform, "browser_start", None)
            return json.dumps(await starter() if starter else {"supported": False}, ensure_ascii=False)
        elif name == "browser_restart":
            restarter = getattr(deps.platform, "browser_restart", None)
            return json.dumps(await restarter() if restarter else {"supported": False}, ensure_ascii=False)
        elif name == "browser_close":
            closer = getattr(deps.platform, "browser_close", None)
            return json.dumps(await closer() if closer else {"supported": False}, ensure_ascii=False)
        elif name.startswith("browser_") and isinstance(deps.platform, BrowserToolProvider):
            return await deps.platform.call_browser_tool(name, args)
        else:
            return f"Unknown tool: {name}"


async def run_codex_coordinator(
    settings: Settings,
    model_specs: list[str] | None = None,
    challenges_root: str = "challenges",
    no_submit: bool = False,
    coordinator_model: str | None = None,
    msg_port: int = 0,
) -> dict[str, Any]:
    """Run the Codex coordinator with the shared event loop."""
    platform, cost_tracker, deps = build_deps(
        settings, model_specs, challenges_root, no_submit,
    )
    deps.msg_port = msg_port
    resolved_model = coordinator_model or "gpt-5.4"
    deps.coordinator_model_spec = f"codex/{resolved_model}"
    coordinator = CodexCoordinator(deps, model=resolved_model)

    async def turn_fn(msg: str) -> None:
        logger.debug(f"Coordinator query: {msg[:200]}")
        await coordinator.turn(msg)
        logger.info("Codex coordinator turn done")

    event_loop_started = False
    deps.defer_trace_close = True
    backend_call_id = (
        deps.tracer.start_operation("backend", "codex_app_server.session")
        if deps.tracer and hasattr(deps.tracer, "start_operation") else None
    )
    backend_error: BaseException | None = None
    try:
        await platform.start()
        await coordinator.start()
        event_loop_started = True
        return await run_event_loop(deps, platform, cost_tracker, turn_fn)
    except BaseException as exc:
        backend_error = exc
        raise
    finally:
        try:
            await _cleanup_step(deps.tracer if backend_call_id else None,
                                "codex_coordinator.stop", coordinator.stop())
        except BaseException as exc:
            backend_error = backend_error or exc
            raise
        finally:
            try:
                if not event_loop_started:
                    await _cleanup_step(deps.tracer if backend_call_id else None,
                                        "platform.close", platform.close())
            except BaseException as exc:
                backend_error = backend_error or exc
                raise
            finally:
                if deps.tracer:
                    if backend_call_id:
                        deps.tracer.end_operation(
                            backend_call_id,
                            "cancelled" if isinstance(backend_error, asyncio.CancelledError)
                            else "error" if backend_error else "completed",
                            error=backend_error,
                        )
                    deps.tracer.close()
