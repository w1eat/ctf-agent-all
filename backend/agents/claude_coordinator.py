"""Claude Agent SDK coordinator — uses the shared event loop with a Claude SDK client."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    create_sdk_mcp_server,
    tool,
)

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


def _coordinator_result_error(message: ResultMessage) -> CoordinatorTurnError | None:
    if not message.is_error:
        return None
    detail = message.result or "; ".join(message.errors or []) or message.subtype
    status = f"HTTP {message.api_error_status}: " if message.api_error_status else ""
    return CoordinatorTurnError(f"Coordinator model error: {status}{detail[:1000]}")

COORDINATOR_PROMPT = """\
You are a CTF competition coordinator running for the ENTIRE duration of a live competition.
Your job is to maximize the number of challenges solved.

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

Platform workflow:
- The platform may be unknown. In auto mode, use the Playwright browser tools to inspect it.
- Always call browser_snapshot before clicking or filling a page element.
- Browser lifecycle is yours to manage through `browser_status`, `browser_start`, and
  `browser_restart`. If a browser tool reports `Connection closed`, call `browser_restart`,
  then take a fresh snapshot before retrying. Use `browser_close` only after all platform
  work is complete; the raw browser close tool is intentionally unavailable.
- For every challenge, first inspect the page and register a normalized record. Set
  `environment_required=true` when the page has a challenge-environment section or a
  start-environment control. Register only real attachment objects; do not treat page
  snapshots, logs, or arbitrary text as files. Include `challenge_url` and any visible
  attachment page/target metadata when available.
- If `environment_required` is true, start the environment in the browser, observe the
  resulting URL, host, or port, and call `set_environment`. A visible start button is not
  an environment until its connection information has been registered.
- Registered challenge packages are prepared automatically. Do not call `spawn_swarm`
  until `get_challenge_state` reports `ready`; the program will enforce this gate.
- Attachment downloads normally run through the platform preparation queue. Use
  `list_attachments`, `download_attachment`, or `import_latest_download` only for
  diagnostics and recovery after inspecting the current page.
- When preparation reports `waiting_for_environment`, inspect the page, start/register
  the environment, and retry preparation. When it reports `needs_input`, repair the
  registration or download metadata and retry before asking the operator.
- Use retry_challenge_preparation after a transient platform or download failure.
- Save only credential-free semantic workflows with save_recipe.
- Never expose cookies, passwords, bearer tokens, or browser storage in messages or recipes.

Challenge-type selection:
- A requested challenge type is a soft preference for your classification, not a fixed category filter.
- Inspect category, name, description, tags, files, connection information, and environment behavior.
- Do not equate generic labels such as `binary` or `exploit` with PWN automatically.
- When a preference is present, classify every candidate yourself and call spawn_swarm only for matching challenges.

You will receive event messages. Respond with tool calls to manage the competition.
"""


def _text(s: str) -> dict:
    """Wrap a string in the Claude SDK MCP tool return format."""
    return {"content": [{"type": "text", "text": s}]}


def _build_coordinator_mcp(deps: CoordinatorDeps):
    """Build MCP server — thin wrappers around coordinator_core functions."""

    @tool("fetch_challenges", "List all challenges with category, points, solve count, and status.", {})
    async def fetch_challenges(args: dict) -> dict:
        return _text(await do_fetch_challenges(deps))

    @tool("prepare_challenge", "Prepare a discovered challenge package for solver agents.", {"challenge_id": str})
    async def prepare_challenge(args: dict) -> dict:
        return _text(await do_prepare_challenge(deps, args["challenge_id"]))

    @tool("start_environment", "Start or retrieve the environment for a challenge.", {"challenge_name": str})
    async def start_environment(args: dict) -> dict:
        return _text(await do_start_environment(deps, args["challenge_name"]))

    @tool("register_challenge", "Register a normalized challenge discovered through the platform browser.", {"data": dict})
    async def register_challenge(args: dict) -> dict:
        return _text(await do_register_challenge(deps, args["data"]))

    @tool("set_environment", "Attach a discovered environment to a challenge.", {"challenge_name": str, "data": dict})
    async def set_environment(args: dict) -> dict:
        return _text(await do_set_environment(deps, args["challenge_name"], args["data"]))

    @tool("list_attachments", "List registered attachment candidates for a challenge.", {"challenge_name": str})
    async def list_attachments(args: dict) -> dict:
        return _text(await do_list_attachments(deps, args["challenge_name"]))

    @tool("download_attachment", "Download one explicitly selected attachment and verify it.", {"challenge_name": str, "attachment_id": str})
    async def download_attachment(args: dict) -> dict:
        return _text(await do_download_attachment(deps, args["challenge_name"], args["attachment_id"]))

    @tool("get_challenge_state", "Get persistent package readiness and attachment state.", {"challenge_name": str})
    async def get_challenge_state(args: dict) -> dict:
        return _text(await do_get_challenge_state(deps, args["challenge_name"]))

    @tool("mark_challenge_needs_input", "Mark a challenge blocked when the platform needs operator input.", {"challenge_name": str, "reason": str})
    async def mark_challenge_needs_input(args: dict) -> dict:
        return _text(await do_mark_needs_input(deps, args["challenge_name"], args["reason"]))

    @tool("retry_challenge_preparation", "Reset a blocked challenge package so attachment/environment preparation can be retried.", {"challenge_name": str})
    async def retry_challenge_preparation(args: dict) -> dict:
        return _text(await do_retry_challenge_preparation(deps, args["challenge_name"]))

    @tool("import_latest_download", "Import the latest Playwright download into challenge distfiles.", {"challenge_name": str, "filename": str})
    async def import_latest_download(args: dict) -> dict:
        return _text(await do_import_download(deps, args["challenge_name"], args.get("filename", "")))

    @tool("save_recipe", "Save a credential-free browser submission workflow. Use steps [{action:'navigate', value:'https://host/challenges/{challenge_id}'}, {action:'type', target:'textarea[aria-label=\"Flag\"]', value:'{flag}', data:{submit:true}}] when Enter submits. Use observed selectors and never submit a test flag.", SAVE_RECIPE_TOOL_SCHEMA)
    async def save_recipe(args: dict) -> dict:
        return _text(await do_save_recipe(deps, args["data"]))

    @tool("browser_status", "Return browser MCP lifecycle status without exposing credentials.", {})
    async def browser_status(args: dict) -> dict:
        getter = getattr(deps.platform, "browser_status", None)
        return _text(json.dumps(await getter() if getter else {"supported": False}, ensure_ascii=False))

    @tool("browser_start", "Start the browser MCP transport if it is stopped.", {})
    async def browser_start(args: dict) -> dict:
        starter = getattr(deps.platform, "browser_start", None)
        return _text(json.dumps(await starter() if starter else {"supported": False}, ensure_ascii=False))

    @tool("browser_restart", "Restart the browser MCP transport after a connection failure.", {})
    async def browser_restart(args: dict) -> dict:
        restarter = getattr(deps.platform, "browser_restart", None)
        return _text(json.dumps(await restarter() if restarter else {"supported": False}, ensure_ascii=False))

    @tool("browser_close", "Close the browser MCP transport after all platform work is complete.", {})
    async def browser_close(args: dict) -> dict:
        closer = getattr(deps.platform, "browser_close", None)
        return _text(json.dumps(await closer() if closer else {"supported": False}, ensure_ascii=False))

    @tool("get_solve_status", "Check which challenges are solved and which swarms are running.", {})
    async def get_solve_status(args: dict) -> dict:
        return _text(await do_get_solve_status(deps))

    @tool("spawn_swarm", "Launch all solver models on a challenge.", {"challenge_name": str})
    async def spawn_swarm(args: dict) -> dict:
        return _text(await do_spawn_swarm(deps, args["challenge_name"]))

    @tool("check_swarm_status", "Get per-agent progress for a swarm.", {"challenge_name": str})
    async def check_swarm_status(args: dict) -> dict:
        return _text(await do_check_swarm_status(deps, args["challenge_name"]))

    @tool("submit_flag", "Submit a flag through the configured platform.", {"challenge_name": str, "flag": str})
    async def submit_flag(args: dict) -> dict:
        return _text(await do_submit_flag(deps, args["challenge_name"], args["flag"]))

    @tool("confirm_submission", "Judge the browser evidence from submit_flag. Confirm only when the page clearly accepts the exact flag.", {"challenge_name": str, "flag": str, "accepted": bool, "reason": str})
    async def confirm_submission(args: dict) -> dict:
        return _text(await do_confirm_submission(deps, args["challenge_name"], args["flag"], args["accepted"], args["reason"]))

    @tool("kill_swarm", "Cancel all agents for a challenge.", {"challenge_name": str})
    async def kill_swarm(args: dict) -> dict:
        return _text(await do_kill_swarm(deps, args["challenge_name"]))

    @tool("bump_agent", "Send targeted insights to a stuck agent.", {"challenge_name": str, "model_spec": str, "insights": str})
    async def bump_agent(args: dict) -> dict:
        return _text(await do_bump_agent(deps, args["challenge_name"], args["model_spec"], args["insights"]))

    @tool("broadcast", "Broadcast a strategic hint to ALL solvers on a challenge.", {"challenge_name": str, "message": str})
    async def broadcast(args: dict) -> dict:
        return _text(await do_broadcast(deps, args["challenge_name"], args["message"]))

    @tool("read_solver_trace", "Read recent trace events from a specific solver. Use this to understand what a solver is doing, what it tried, and where it's stuck.", {"challenge_name": str, "model_spec": str, "last_n": int})
    async def read_solver_trace(args: dict) -> dict:
        return _text(await do_read_solver_trace(deps, args["challenge_name"], args["model_spec"], args.get("last_n", 20)))

    coordinator_tools = [
        fetch_challenges, get_solve_status, spawn_swarm, check_swarm_status,
        submit_flag, confirm_submission, kill_swarm, bump_agent, broadcast, read_solver_trace,
        prepare_challenge, start_environment, register_challenge,
        set_environment, list_attachments, download_attachment, get_challenge_state,
        mark_challenge_needs_input, retry_challenge_preparation,
        import_latest_download, save_recipe,
        browser_status, browser_start, browser_restart, browser_close,
    ]

    if bool(getattr(deps.settings, "coordinator_full_access", False)):
        @tool(
            "coordinator_shell",
            "Run an unrestricted command in the host shell and return stdout, stderr, and exit code.",
            {"command": str, "cwd": str, "timeout_seconds": float},
        )
        async def coordinator_shell(args: dict) -> dict:
            return _text(
                await do_coordinator_shell(
                    deps,
                    args.get("command", ""),
                    args.get("cwd", ""),
                    args.get("timeout_seconds", 120),
                )
            )

        coordinator_tools.append(coordinator_shell)

    return create_sdk_mcp_server(
        name="coordinator", version="1.0.0", tools=coordinator_tools,
    )


def _build_playwright_mcp(deps: CoordinatorDeps):
    """Expose the safe Playwright subset through Claude's SDK MCP."""
    provider = deps.platform
    if not isinstance(provider, BrowserToolProvider):
        return None
    tools = []
    for spec in provider.browser_tool_specs():
        name = spec["name"]
        schema = spec.get("inputSchema", {"type": "object", "properties": {}})
        description = spec.get("description", "Playwright browser operation")

        async def handler(args: dict, _name=name) -> dict:
            return _text(await provider.call_browser_tool(_name, args))

        tools.append(tool(name, description, schema)(handler))
    return create_sdk_mcp_server(name="playwright", version="1.0.0", tools=tools)


async def run_claude_coordinator(
    settings: Settings,
    model_specs: list[str] | None = None,
    challenges_root: str = "challenges",
    no_submit: bool = False,
    coordinator_model: str | None = None,
    msg_port: int = 0,
) -> dict[str, Any]:
    """Run the Claude Agent SDK coordinator with the shared event loop."""
    platform, cost_tracker, deps = build_deps(
        settings, model_specs, challenges_root, no_submit,
    )
    deps.msg_port = msg_port
    try:
        await platform.start()
    except BaseException:
        await platform.close()
        if deps.tracer:
            deps.tracer.close()
        raise

    try:
        mcp_server = _build_coordinator_mcp(deps)
        playwright_mcp = _build_playwright_mcp(deps)
        browser_provider = platform if isinstance(platform, BrowserToolProvider) else None
        resolved_model = coordinator_model or "claude-opus-4-6"
        deps.coordinator_model_spec = f"claude-sdk/{resolved_model}"
        full_access = bool(getattr(settings, "coordinator_full_access", False))

        allowed = {
            "mcp__coordinator__fetch_challenges", "mcp__coordinator__get_solve_status",
            "mcp__coordinator__spawn_swarm", "mcp__coordinator__check_swarm_status",
            "mcp__coordinator__submit_flag", "mcp__coordinator__confirm_submission", "mcp__coordinator__kill_swarm",
            "mcp__coordinator__bump_agent", "mcp__coordinator__broadcast",
            "mcp__coordinator__read_solver_trace",
            "mcp__coordinator__prepare_challenge", "mcp__coordinator__start_environment",
            "mcp__coordinator__register_challenge", "mcp__coordinator__set_environment",
            "mcp__coordinator__list_attachments", "mcp__coordinator__download_attachment",
            "mcp__coordinator__get_challenge_state", "mcp__coordinator__mark_challenge_needs_input",
            "mcp__coordinator__retry_challenge_preparation",
            "mcp__coordinator__import_latest_download", "mcp__coordinator__save_recipe",
            "mcp__coordinator__browser_status", "mcp__coordinator__browser_start",
            "mcp__coordinator__browser_restart", "mcp__coordinator__browser_close",
            "ToolSearch",
            "TaskCreate", "TaskUpdate", "TaskGet", "TaskList", "TaskOutput", "TaskStop",
        }

        if full_access:
            allowed.add("mcp__coordinator__coordinator_shell")

        async def enforce_allowlist(input_data, tool_use_id, context):
            if input_data.get("hook_event_name") != "PreToolUse":
                return {}
            tool = input_data.get("tool_name", "")
            if deps.tracer:
                deps.tracer.tool_call(tool, input_data.get("tool_input", {}),
                                      call_id=tool_use_id)
            if full_access:
                return {}
            if tool in allowed:
                return {}
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"{tool} not available to coordinator.",
                }
            }

        async def audit_tool_result(input_data, tool_use_id, context):
            if input_data.get("hook_event_name") == "PostToolUse" and deps.tracer:
                deps.tracer.tool_result(
                    input_data.get("tool_name", ""),
                    input_data.get("tool_response", ""),
                    call_id=tool_use_id,
                )
            return {}

        async def audit_tool_failure(input_data, tool_use_id, context):
            if input_data.get("hook_event_name") == "PostToolUseFailure" and deps.tracer:
                deps.tracer.end_operation(
                    tool_use_id,
                    "interrupted" if input_data.get("is_interrupt") else "error",
                    output=input_data.get("error"),
                    tool=input_data.get("tool_name", ""),
                )
            return {}

        mcp_servers = {"coordinator": mcp_server}
        if playwright_mcp and browser_provider:
            mcp_servers["playwright"] = playwright_mcp
            allowed.update(
                f"mcp__playwright__{spec['name']}"
                for spec in browser_provider.browser_tool_specs()
            )

        options = ClaudeAgentOptions(
            model=resolved_model,
            tools={"type": "preset", "preset": "claude_code"} if full_access else None,
            system_prompt=COORDINATOR_PROMPT,
            env={"CLAUDECODE": ""},
            mcp_servers=mcp_servers,
            allowed_tools=list(allowed),
            permission_mode="bypassPermissions",
            hooks={
                "PreToolUse": [HookMatcher(hooks=[enforce_allowlist])],
                "PostToolUse": [HookMatcher(hooks=[audit_tool_result])],
                "PostToolUseFailure": [HookMatcher(hooks=[audit_tool_failure])],
            },
        )
    except BaseException:
        await platform.close()
        if deps.tracer:
            deps.tracer.close()
        raise

    event_loop_started = False
    deps.defer_trace_close = True
    backend_call_id = (
        deps.tracer.start_operation("backend", "claude_sdk.session")
        if deps.tracer and hasattr(deps.tracer, "start_operation") else None
    )
    backend_error: BaseException | None = None
    try:
        async with ClaudeSDKClient(options=options) as client:
            async def turn_fn(msg: str) -> None:
                logger.debug(f"Coordinator query: {msg[:200]}")
                if deps.tracer:
                    deps.tracer.turn_input(msg)
                    turn_call_id = deps.tracer.start_operation("turn", "claude", msg,
                                                              session_state="connected")
                else:
                    turn_call_id = None
                async def consume() -> None:
                    await client.query(msg)
                    msg_count = 0
                    async for message in client.receive_response():
                        msg_count += 1
                        msg_type = type(message).__name__
                        logger.debug(f"Coordinator received: {msg_type}")
                        if deps.tracer:
                            deps.tracer.event("llm_message", message_type=msg_type, text=str(message))
                        if isinstance(message, ResultMessage):
                            cost = getattr(message, "total_cost_usd", 0)
                            session = getattr(message, "session_id", None)
                            logger.info(
                                "Claude coordinator turn done (messages=%s, cost=$%.4f, session=%s)",
                                msg_count,
                                cost,
                                session,
                            )
                            if deps.tracer:
                                deps.tracer.event(
                                    "turn_completed",
                                    messages=msg_count,
                                    cost_usd=cost,
                                    session_id=session,
                                )
                            error = _coordinator_result_error(message)
                            if error:
                                raise error
                    if msg_count == 0:
                        logger.warning("Coordinator turn produced no messages!")

                timeout_s = int(settings.coordinator_decision_timeout_seconds)
                try:
                    await asyncio.wait_for(consume(), timeout=timeout_s if timeout_s > 0 else None)
                    if deps.tracer and turn_call_id:
                        deps.tracer.end_operation(turn_call_id, "completed")
                except TimeoutError:
                    logger.warning("Claude coordinator turn timed out after %ss", timeout_s)
                    if deps.tracer:
                        deps.tracer.event("turn_timeout", timeout_seconds=timeout_s)
                        if turn_call_id:
                            deps.tracer.end_operation(turn_call_id, "timeout")
                    raise CoordinatorTurnError(f"Coordinator turn timed out after {timeout_s}s") from None
                except BaseException as exc:
                    if deps.tracer and turn_call_id:
                        deps.tracer.end_operation(turn_call_id,
                                                  "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                                  error=exc)
                    raise

            event_loop_started = True
            return await run_event_loop(deps, platform, cost_tracker, turn_fn)
    except BaseException as exc:
        backend_error = exc
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
    raise RuntimeError("Claude coordinator exited without a result")
