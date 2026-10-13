"""Playwright MCP transport and browser-first platform adapter."""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import logging
import os
import re
import shutil
import time
import traceback
import uuid
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from mcp.client.stdio import stdio_client
from pydantic import ValidationError

from backend.platforms.environments import LocalEnvironmentManager
from backend.platforms.models import (
    AttachmentMetadata,
    ChallengeBundle,
    ChallengeMode,
    ChallengeState,
    EnvironmentInfo,
    PlatformProfile,
    SubmissionResult,
)
from backend.platforms.recipes import (
    PlatformRecipe,
    RecipeStore,
    redact_sensitive_text,
    submission_recipe_issue,
)
from backend.platforms.state import (
    AttachmentArtifact,
    AttachmentCandidate,
    ChallengeStateStore,
)
from mcp import ClientSession, StdioServerParameters

logger = logging.getLogger(__name__)

# MCP tool results are text; cap in-band binary transfer to protect memory/logs.
MAX_AUTH_TRANSFER_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class PendingSubmission:
    flag: str
    submitted_at: float
    initial_evidence: str


@dataclass(frozen=True)
class SubmissionConfirmation:
    challenge_id: str
    flag: str
    accepted: bool
    reason: str
    evidence: str
    success_markers: tuple[str, ...]
    failure_markers: tuple[str, ...]
    confirmed_at: float


class PlaywrightToolDiscoveryError(RuntimeError):
    """Raised when the configured Playwright MCP cannot expose its tools."""


class BrowserProfileInUseError(RuntimeError):
    """Raised when another process already holds the Chromium profile directory."""


# Chromium refuses to start when another process holds the same --user-data-dir; the
# Playwright MCP reports that as an in-band tool error result rather than an exception.
PROFILE_IN_USE_MARKER = "browser is already in use"


ALLOWED_BROWSER_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_find",
    "browser_click",
    "browser_type",
    "browser_fill_form",
    "browser_wait_for",
    "browser_tabs",
    "browser_network_requests",
    "browser_network_request",
    "browser_evaluate",
    "browser_take_screenshot",
    "browser_close",
}

BROWSER_TOOL_SCHEMAS = [
    {"name": "browser_navigate", "description": "Navigate to a platform or target URL.", "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "browser_snapshot", "description": "Capture the current accessibility snapshot.", "inputSchema": {"type": "object", "properties": {"boxes": {"type": "boolean"}, "depth": {"type": "integer"}, "filename": {"type": "string"}, "target": {"type": "string"}}}},
    {"name": "browser_find", "description": "Find text or a regular expression in the latest page snapshot.", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}, "regex": {"type": "string"}}}},
    {"name": "browser_click", "description": "Click an element from the latest snapshot.", "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}, "element": {"type": "string"}, "button": {"type": "string"}, "doubleClick": {"type": "boolean"}, "modifiers": {"type": "array", "items": {"type": "string"}}}, "required": ["target"]}},
    {"name": "browser_type", "description": "Type into an element from the latest snapshot.", "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}, "text": {"type": "string"}, "element": {"type": "string"}, "slowly": {"type": "boolean"}, "submit": {"type": "boolean"}}, "required": ["target", "text"]}},
    {"name": "browser_fill_form", "description": "Fill multiple form fields.", "inputSchema": {"type": "object", "properties": {"fields": {"type": "array"}}, "required": ["fields"]}},
    {"name": "browser_wait_for", "description": "Wait for text or time.", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}, "textGone": {"type": "string"}, "time": {"type": "number"}}}},
    {"name": "browser_tabs", "description": "List, create, close, or select browser tabs.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "index": {"type": "integer"}, "url": {"type": "string"}}, "required": ["action"]}},
    {"name": "browser_network_requests", "description": "Inspect requests made by the current page.", "inputSchema": {"type": "object", "properties": {"filter": {"type": "string"}, "static": {"type": "boolean"}, "filename": {"type": "string"}}}},
    {"name": "browser_network_request", "description": "Inspect one request from browser_network_requests.", "inputSchema": {"type": "object", "properties": {"index": {"type": "integer"}, "part": {"type": "string"}, "filename": {"type": "string"}}, "required": ["index"]}},
    {"name": "browser_evaluate", "description": "Evaluate a read-only extraction function on the page.", "inputSchema": {"type": "object", "properties": {"function": {"type": "string"}, "target": {"type": "string"}, "element": {"type": "string"}, "filename": {"type": "string"}}, "required": ["function"]}},
    {"name": "browser_take_screenshot", "description": "Capture a browser screenshot for evidence.", "inputSchema": {"type": "object", "properties": {"filename": {"type": "string"}, "fullPage": {"type": "boolean"}, "scale": {"type": "string"}, "type": {"type": "string"}, "target": {"type": "string"}}}},
    {"name": "browser_close", "description": "Close the browser page.", "inputSchema": {"type": "object", "properties": {}}},
]

_SNAPSHOT_REQUIRED = {
    "browser_click",
    "browser_type",
    "browser_fill_form",
    "browser_press_key",
    "browser_select_option",
    "browser_hover",
    "browser_drag",
}
_SNAPSHOT_INVALIDATING = {
    "browser_navigate",
    "browser_navigate_back",
    "browser_click",
    "browser_tabs",
}

MCP_START_TIMEOUT_SECONDS = 120.0
MCP_STOP_TIMEOUT_SECONDS = 20.0


def _settle(future: asyncio.Future[None], error: BaseException | None = None) -> None:
    """Hand a lifecycle command's outcome to its waiting caller exactly once."""
    if future.done():
        return
    if error is None:
        future.set_result(None)
    else:
        future.set_exception(error)


def _consume_future(future: asyncio.Future[Any]) -> None:
    """Retrieve a result its caller may never await, so it is not logged as unretrieved."""
    if not future.cancelled():
        future.exception()


class BrowserMCPClient:
    """Small MCP client that keeps one Playwright browser process alive."""

    def __init__(
        self,
        base_url: str,
        profile_dir: str,
        download_dir: str,
        *,
        command: str = "",
        command_args: list[str] | None = None,
        browser: str = "chrome",
        executable_path: str = "",
        headless: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.profile_dir = Path(profile_dir).resolve()
        self.download_dir = Path(download_dir).resolve()
        self.command = command
        self.command_args = command_args
        self.browser = browser
        self.executable_path = executable_path
        self.headless = headless
        self._session: ClientSession | None = None
        self._allowed_origins: set[str] = set()
        self._snapshot_valid = False
        self._tool_specs: dict[str, dict[str, Any]] = {}
        self._lifecycle_lock = asyncio.Lock()
        self._commands: asyncio.Queue[tuple[str, asyncio.Future[None]]] = asyncio.Queue()
        self._owner_task: asyncio.Task[None] | None = None
        self._owner_error: BaseException | None = None
        self._last_error = ""
        self._reconnect_count = 0
        self._profile_blocked: str | None = None
        self.tracer: Any | None = None

    async def start(self, *, parent_call_id: str | None = None) -> None:
        call_id = self.tracer.start_operation("mcp_lifecycle", "playwright.start",
                                              {"command": self.command, "args": self.command_args},
                                              session_state="started" if self._session else "stopped",
                                              parent_call_id=parent_call_id) if self.tracer else None
        try:
            await self._command("start")
        except BaseException as exc:
            if call_id:
                self.tracer.end_operation(call_id, "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                          error=exc, session_state="started" if self._session else "stopped")
            raise
        else:
            if call_id:
                self.tracer.end_operation(call_id, "completed", session_state="started" if self._session else "stopped")

    async def _command(self, kind: str) -> None:
        """Ask the owner task to establish, cycle, or drop the MCP connection.

        AnyIO requires the stdio and session contexts to be entered and exited by the
        same task, so every caller funnels through this queue - coordinator turns, MCP
        tool dispatch, and preparation workers alike.
        """
        limit = MCP_STOP_TIMEOUT_SECONDS if kind == "stop" else MCP_START_TIMEOUT_SECONDS
        async with self._lifecycle_lock:
            owner = self._owner_task
            running = owner is not None and not owner.done()
            if kind == "stop" and not running:
                self._owner_task = None
                self._reset_session()
                return
            if kind == "start" and running and self._session is not None:
                return
            if not running:
                self._owner_task = asyncio.create_task(
                    self._owner_loop(), name="playwright-mcp-owner"
                )
            ready: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            ready.add_done_callback(_consume_future)
            self._commands.put_nowait((kind, ready))
            try:
                await asyncio.wait_for(asyncio.shield(ready), timeout=limit)
            except TimeoutError:
                self._last_error = f"Playwright MCP {kind} timed out after {limit:g}s"
                raise
            if kind == "stop":
                task, self._owner_task = self._owner_task, None
                self._reset_session()
                if task is not None:
                    await asyncio.gather(task, return_exceptions=True)

    def _reset_session(self) -> None:
        self._session = None
        self._tool_specs = {}

    async def _owner_loop(self) -> None:
        """Own the MCP connection for as long as this client lives.

        Only this task ever enters or exits the stdio and session contexts; the
        connection stays open while it waits here for the next lifecycle command.
        """
        pending: tuple[str, asyncio.Future[None]] | None = None
        while True:
            if pending is None:
                pending = await self._commands.get()
            kind, ready = pending
            pending = None
            if kind == "stop":
                _settle(ready)
                return
            if kind == "start" and self._session is not None:
                _settle(ready)
                continue
            if kind == "restart":
                self._reset_session()
            try:
                async with AsyncExitStack() as stack:
                    await self._connect(stack)
                    self._owner_error = None
                    if kind == "restart":
                        self._reconnect_count += 1
                    _settle(ready)
                    pending = await self._commands.get()
            except BaseException as exc:
                self._owner_error = exc
                self._reset_session()
                _settle(ready, exc)
                if isinstance(exc, asyncio.CancelledError):
                    raise

    async def _connect(self, stack: AsyncExitStack) -> None:
        params = self._server_params()
        read_stream, write_stream = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        tools_result = await session.list_tools()
        self._load_tool_catalog(tools_result.tools)
        self._session = session
        logger.info(
            "Playwright MCP tool catalog loaded: version=0.0.82 tools=%s",
            ",".join(sorted(self._tool_specs)),
        )
        self.allow_origin(self.base_url)
        self._last_error = ""
        logger.info("Playwright MCP connected using %s", params.command)

    def _server_params(self) -> StdioServerParameters:
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        command = self.command or shutil.which("npx") or shutil.which("npx.cmd") or "npx"
        args = list(self.command_args or ["-y", "@playwright/mcp@0.0.82"])
        if "--browser" not in args:
            args.extend(["--browser", self.browser])
        if self.executable_path and "--executable-path" not in args:
            args.extend(["--executable-path", self.executable_path])
        if "--user-data-dir" not in args:
            args.extend(["--user-data-dir", str(self.profile_dir)])
        if "--output-dir" not in args:
            args.extend(["--output-dir", str(self.download_dir)])
        if self.headless and "--headless" not in args:
            args.append("--headless")
        return StdioServerParameters(command=command, args=args, env=dict(os.environ))

    async def restart(self, *, parent_call_id: str | None = None) -> None:
        """Restart the MCP transport and browser context after a disconnect."""
        call_id = self.tracer.start_operation("mcp_lifecycle", "playwright.restart",
                                              session_state="started" if self._session else "stopped",
                                              parent_call_id=parent_call_id) if self.tracer else None
        try:
            await self._command("restart")
        except BaseException as exc:
            if call_id:
                self.tracer.end_operation(call_id, "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                          error=exc, session_state="started" if self._session else "stopped")
            raise
        else:
            if call_id:
                self.tracer.end_operation(call_id, "completed", session_state="started" if self._session else "stopped")

    def status(self) -> dict[str, Any]:
        return {
            "started": self._session is not None,
            "tool_catalog_loaded": bool(self._tool_specs),
            "base_url": self.base_url,
            "browser": self.browser,
            "profile_dir": str(self.profile_dir),
            "download_dir": str(self.download_dir),
            "reconnect_count": self._reconnect_count,
            "last_error": self._last_error,
        }

    def _load_tool_catalog(self, tools: list[Any]) -> None:
        self._tool_specs = {
            tool.name: {
                "name": tool.name,
                "description": tool.description or "Playwright browser operation",
                "inputSchema": tool.input_schema,
            }
            for tool in tools
        }
        required = {
            "browser_navigate",
            "browser_snapshot",
            "browser_click",
            "browser_find",
            "browser_wait_for",
            "browser_tabs",
        }
        missing = sorted(required - self._tool_specs.keys())
        if missing:
            self._tool_specs = {}
            raise PlaywrightToolDiscoveryError(
                f"Playwright MCP is missing required tools: {', '.join(missing)}"
            )

    def allow_origin(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            self._allowed_origins.add(f"{parsed.scheme}://{parsed.netloc}".lower())

    def _check_url(self, url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return "Only absolute HTTP(S) URLs are allowed."
        origin = f"{parsed.scheme}://{parsed.netloc}".lower()
        if origin not in self._allowed_origins:
            return f"URL origin is not allowlisted: {origin}"
        return None

    async def call(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        call_id = self.tracer.start_operation("mcp_tool", name, arguments,
                                              session_state="started" if self._session else "stopped") if self.tracer else None
        try:
            result = await self._call_inner(name, arguments, trace_call_id=call_id)
        except BaseException as exc:
            if call_id:
                self.tracer.end_operation(call_id, "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                          error=exc, session_state="started" if self._session else "stopped")
            raise
        else:
            if call_id:
                status = "error" if result.startswith("Playwright MCP error:") else "completed"
                self.tracer.end_operation(call_id, status, output=result,
                                          session_state="started" if self._session else "stopped")
            return result

    async def _call_inner(self, name: str, arguments: dict[str, Any] | None = None,
                          *, trace_call_id: str | None = None) -> str:
        if self._profile_blocked:
            return self._profile_blocked
        if not self._session:
            try:
                await self.start()
            except Exception as exc:
                self._last_error = str(exc)
                return f"Playwright MCP error: {exc}"
        session = self._session
        if session is None:
            return "Playwright MCP error: session is unavailable after startup"
        if name not in self._tool_specs:
            return f"Browser tool is not available in the discovered MCP catalog: {name}"
        arguments = arguments or {}
        if name == "browser_navigate":
            error = self._check_url(str(arguments.get("url", "")))
            if error:
                return f"Navigation blocked: {error}"
        if name in _SNAPSHOT_REQUIRED and not self._snapshot_valid:
            return "Call browser_snapshot before interacting with an element."
        started = time.monotonic()
        try:
            result = await session.call_tool(name, arguments)
        except Exception as exc:
            self._snapshot_valid = False
            self._last_error = str(exc)
            logger.warning("Playwright tool failed: %s error=%s", name, exc)
            if self.tracer:
                self.tracer.event("mcp_connection_failed", tool=name,
                                  call_id=trace_call_id,
                                  error_type=type(exc).__name__, error=str(exc),
                                  traceback="".join(traceback.format_exception(exc)),
                                  session_state="started" if self._session else "stopped")
            if self._is_connection_error(exc):
                try:
                    await self.restart(parent_call_id=trace_call_id)
                    session = self._session
                    if session is None:
                        raise ConnectionError("Playwright MCP session is unavailable after reconnect")
                    result = await session.call_tool(name, arguments)
                    self._last_error = ""
                except Exception as reconnect_exc:
                    self._last_error = str(reconnect_exc)
                    logger.warning("Playwright MCP reconnect failed: %s", reconnect_exc)
                    return f"Playwright MCP error: {reconnect_exc}"
            else:
                return f"Playwright MCP error: {exc}"
        if name == "browser_snapshot":
            self._snapshot_valid = True
        elif name in _SNAPSHOT_INVALIDATING:
            self._snapshot_valid = False
        formatted = self._format_result(result)
        logger.debug(
            "Playwright tool completed: %s duration=%.3fs error=%s",
            name,
            time.monotonic() - started,
            self._result_is_error(result),
        )
        if self._result_is_error(result) and PROFILE_IN_USE_MARKER in formatted.casefold():
            self._block_on_profile_conflict()
            return self._profile_blocked or formatted
        return formatted

    def _block_on_profile_conflict(self) -> None:
        """Stop later browser calls from retrying a profile another run holds."""
        self._profile_blocked = (
            f"Browser profile {self.profile_dir} is already in use by another process, so no "
            "browser tool can work in this run. Do not call browser_restart, browser_start or "
            "browser_close; none of them can release it. Report this to the operator: the other "
            "ctf-solve run has to exit, or this run has to be restarted with --browser-profile "
            "pointing at a different directory."
        )
        self._last_error = self._profile_blocked
        logger.error("Playwright profile is already in use: %s", self.profile_dir)

    def profile_blocked_reason(self) -> str | None:
        return self._profile_blocked

    @staticmethod
    def _is_connection_error(exc: Exception) -> bool:
        text = str(exc).casefold()
        return any(
            marker in text
            for marker in (
                "connection closed",
                "closed resource",
                "session is closed",
                "broken pipe",
                "eof",
                "stdio stream",
            )
        )

    @staticmethod
    def _result_is_error(result: Any) -> bool:
        return bool(getattr(result, "is_error", False))

    @staticmethod
    def _format_result(result: Any) -> str:
        parts: list[str] = []
        for item in getattr(result, "content", []) or []:
            text = getattr(item, "text", None)
            if text:
                parts.append(redact_sensitive_text(str(text)))
            elif getattr(item, "type", "") == "image":
                parts.append("[image artifact returned]")
            elif getattr(item, "type", "") == "resource":
                resource = getattr(item, "resource", None)
                resource_text = getattr(resource, "text", None)
                if resource_text:
                    parts.append(str(resource_text))
        structured = getattr(result, "structured_content", None)
        if not parts and structured is not None:
            parts.append(json.dumps(structured, ensure_ascii=True, default=str))
        if BrowserMCPClient._result_is_error(result):
            parts.insert(0, "ERROR")
        return "\n".join(parts) or "(no output)"

    def browser_tool_specs(self) -> list[dict]:
        if not self._tool_specs:
            raise PlaywrightToolDiscoveryError("Playwright MCP tool catalog is not loaded")
        # Lifecycle is controlled through coordinator tools so the model cannot
        # silently destroy the transport with the raw browser_close tool.
        return [spec for name, spec in self._tool_specs.items() if name != "browser_close"]

    async def close(self, *, parent_call_id: str | None = None) -> None:
        call_id = self.tracer.start_operation("mcp_lifecycle", "playwright.close",
                                              session_state="started" if self._session else "stopped",
                                              parent_call_id=parent_call_id) if self.tracer else None
        try:
            await self._close_inner()
        except BaseException as exc:
            if call_id:
                self.tracer.end_operation(call_id, "cancelled" if isinstance(exc, asyncio.CancelledError) else "error",
                                          error=exc, session_state="started" if self._session else "stopped")
            raise
        else:
            if call_id:
                self.tracer.end_operation(call_id, "completed", session_state="started" if self._session else "stopped")

    async def _close_inner(self) -> None:
        await self._command("stop")


class BrowserAutoPlatformAdapter:
    """Browser-first adapter whose challenge workflow is driven by the coordinator."""

    browser_submission = True

    def __init__(self, settings: Any, challenges_root: str = "challenges", *, allow_submit: bool = False) -> None:
        self.settings = settings
        self.root = Path(challenges_root).resolve()
        self.base_url = (settings.platform_url or settings.ctfd_url).rstrip("/")
        self.allow_submit = allow_submit
        self.state = ChallengeStateStore(
            getattr(settings, "challenge_state_db_path", ".runtime/challenge_state.sqlite3"),
            run_id=getattr(settings, "challenge_run_id", "") or uuid.uuid4().hex,
        )
        self.browser = BrowserMCPClient(
            self.base_url,
            settings.browser_profile_dir,
            str(Path(settings.browser_download_dir).resolve() / self.state.run_id),
            command=settings.playwright_mcp_command,
            command_args=settings.playwright_mcp_args,
            browser=settings.playwright_browser,
            executable_path=settings.playwright_executable_path,
            headless=settings.playwright_headless,
        )
        self.browser.allow_origin(self.base_url)
        self.recipes = RecipeStore(settings.platform_recipe_dir)
        self._bundles: dict[str, ChallengeBundle] = {}
        self._directories: dict[str, Path] = {}
        self._solved: set[str] = set()
        self._pending_submissions: dict[str, PendingSubmission] = {}
        self._submission_confirmations: list[SubmissionConfirmation] = []
        self._environments = LocalEnvironmentManager(self.root)
        self._browser_action_lock = asyncio.Lock()
        self._download_claim_lock = asyncio.Lock()
        self._claimed_downloads: set[Path] = set()

    async def start(self) -> None:
        if not self.base_url:
            raise RuntimeError("--platform-url or PLATFORM_URL is required for auto platform mode")
        self.root.mkdir(parents=True, exist_ok=True)
        self._restore_state()
        await self.browser.start()
        if self.settings.platform_login:
            await self.browser.call("browser_navigate", {"url": self.base_url})
            await self.browser.call("browser_snapshot", {})
            if blocked := self.browser.profile_blocked_reason():
                logger.error("%s", blocked)
                raise BrowserProfileInUseError(
                    f"浏览器 profile 被其它进程占用，无法打开 Playwright 浏览器：{self.browser.profile_dir}\n"
                    "请先退出另一个 ctf-solve 进程；或用 --browser-profile 指定另一个目录后重跑。"
                )
            await asyncio.to_thread(input, "Complete platform login in the Playwright browser, then press Enter here: ")

    def _restore_state(self) -> None:
        """Restore only challenges belonging to the selected persisted run."""
        for row in self.state.list_challenges():
            metadata = Path(row["package_dir"]) / "metadata.yml"
            if not metadata.is_file():
                continue
            try:
                data = yaml.safe_load(metadata.read_text(encoding="utf-8")) or {}
                needs_migration = any(
                    not isinstance(item, str)
                    or not item.replace("\\", "/").startswith("distfiles/")
                    for item in data.get("files", []) or []
                )
                bundle = ChallengeBundle.from_metadata(data, platform=row.get("platform") or "browser-auto")
                bundle = bundle.model_copy(
                    update={
                        "native_id": row["native_id"],
                        "state": row["state"],
                        "reason": row.get("reason", ""),
                    }
                ).normalized()
                if (
                    bundle.state == ChallengeState.NEEDS_INPUT
                    and "no browser target or source URL" in bundle.reason
                ):
                    bundle = bundle.model_copy(
                        update={
                            "state": ChallengeState.WAITING_FOR_DECISION,
                            "reason": "requeued after incomplete attachment metadata",
                        }
                    ).normalized()
            except (OSError, ValueError, yaml.YAMLError):
                logger.warning("Could not restore challenge state for %s", row.get("name"), exc_info=True)
                continue
            previous = self._bundles.get(bundle.name)
            if previous and previous.native_id != bundle.native_id:
                raise ValueError(f"Duplicate challenge name {bundle.name!r} in persisted run")
            self._bundles[bundle.name] = bundle
            self._directories[bundle.name] = Path(row["package_dir"])
            restored_candidates = self._build_attachment_candidates(bundle)
            for candidate in restored_candidates:
                self.state.upsert_attachment(bundle.native_id, candidate)
            bundle = self._migrate_existing_artifacts(bundle, restored_candidates)
            if bundle.state == ChallengeState.READY and not self._attachments_ready(bundle):
                bundle = self._set_bundle_state(bundle, self._readiness_state(bundle),
                                                "saved attachment failed integrity check")
            if bundle.state == ChallengeState.SOLVED:
                self._solved.add(bundle.name)
            if needs_migration:
                temporary = metadata.with_suffix(".yml.tmp")
                temporary.write_text(
                    yaml.safe_dump(bundle.metadata_dict(), allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                temporary.replace(metadata)

    async def discover(self) -> PlatformProfile:
        await self.browser.call("browser_navigate", {"url": self.base_url})
        snapshot = await self.browser.call("browser_snapshot", {})
        authenticated = not any(marker in snapshot.lower() for marker in ("sign in", "log in", "登录"))
        return PlatformProfile(
            name="browser-auto",
            origin=self.base_url,
            authenticated=authenticated,
            capabilities={"browser", "discover", "download", "remote_environment", "local_environment"},
            evidence=[snapshot[:1000]],
        )

    async def list_challenges(self) -> list[ChallengeBundle]:
        return [bundle.normalized() for bundle in self._bundles.values()]

    def _slug(self, name: str) -> str:
        slug = re.sub(r'[<>:"/\\|?*\.\x00-\x1f]', "", name.lower().strip())
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug or "challenge"

    def _write_bundle(self, bundle: ChallengeBundle) -> ChallengeBundle:
        bundle = bundle.normalized()
        previous = self._bundles.get(bundle.name)
        if previous and previous.native_id != bundle.native_id:
            raise ValueError(
                f"Duplicate challenge name {bundle.name!r} has IDs "
                f"{previous.native_id!r} and {bundle.native_id!r}; registration refused"
            )
        directory = self.root / self._slug(bundle.name)
        for existing_name, existing_directory in self._directories.items():
            if existing_name != bundle.name and existing_directory == directory:
                raise ValueError(
                    f"Challenge names {existing_name!r} and {bundle.name!r} "
                    "collide after directory normalization"
                )
        if directory.exists() and self.state.get_challenge(bundle.native_id) is None:
            backup_root = self.state.path.parent / "legacy-backup" / self.state.run_id
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / directory.name
            if backup.exists():
                backup = backup_root / f"{directory.name}-{int(time.time())}-{uuid.uuid4().hex[:6]}"
            shutil.move(str(directory), str(backup))
        directory.mkdir(parents=True, exist_ok=True)
        metadata = directory / "metadata.yml"
        temporary = metadata.with_suffix(".yml.tmp")
        temporary.write_text(
            yaml.safe_dump(bundle.metadata_dict(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        temporary.replace(metadata)
        self.state.upsert_challenge(
            native_id=bundle.native_id,
            name=bundle.name,
            slug=self._slug(bundle.name),
            platform=bundle.platform,
            mode=bundle.mode.value,
            package_dir=str(directory),
            connection_info=bundle.connection_info,
            environment=bundle.environment,
            state=bundle.state.value,
            reason=bundle.reason,
        )
        self._bundles[bundle.name] = bundle
        self._directories[bundle.name] = directory
        return bundle

    @staticmethod
    def _attachment_strength(item: Any) -> int:
        normalized = AttachmentMetadata.from_raw(item)
        return (4 if normalized.has_exact_source_url else 0) + (2 if normalized.sha256 else 0) + (1 if normalized.size is not None else 0)

    def _merge_registered_bundle(self, existing: ChallengeBundle, incoming: ChallengeBundle) -> ChallengeBundle:
        """Retain verified package state when discovery registers the same ID again."""
        old_items = [dict(x) for x in existing.source_data.get("attachments") or [] if isinstance(x, dict)]
        new_items = [dict(x) for x in incoming.source_data.get("attachments") or [] if isinstance(x, dict)]
        old_by_name: dict[str, list[int]] = {}
        for index, item in enumerate(old_items):
            old_by_name.setdefault(AttachmentMetadata.from_raw(item).name, []).append(index)
        used: set[int] = set()
        attachments: list[dict[str, Any]] = []
        for new in new_items:
            normalized = AttachmentMetadata.from_raw(new)
            matching_id = [i for i, old in enumerate(old_items) if i not in used and
                           AttachmentMetadata.from_raw(old).attachment_id == normalized.attachment_id and
                           normalized.attachment_id not in {"0", "1"}]
            matching_name = [i for i in old_by_name.get(normalized.name, []) if i not in used]
            match = (matching_id or matching_name) if len(matching_id or matching_name) == 1 else []
            if match:
                index = match[0]
                used.add(index)
                old = old_items[index]
                if (self._attachment_strength(new) > self._attachment_strength(old) or
                    (self._attachment_strength(new) == self._attachment_strength(old) and
                     AttachmentMetadata.from_raw(new).has_exact_source_url and
                     AttachmentMetadata.from_raw(new).sha256 != AttachmentMetadata.from_raw(old).sha256)):
                    attachments.append(new)
                else:
                    attachments.append({
                        **old,
                        **({"target": new["target"]} if new.get("target") else {}),
                        **({"challenge_page_url": new["challenge_page_url"]}
                           if new.get("challenge_page_url") else {}),
                    })
            else:
                attachments.append(new)
        # A complete replacement manifest supersedes removed entries. Sparse
        # coordinator registrations may only omit previously known attachments.
        replacement_manifest = bool(new_items) and all(
            self._attachment_strength(item) >= 7 for item in new_items
        )
        if not replacement_manifest:
            attachments.extend(old for index, old in enumerate(old_items)
                               if index not in used and self._attachment_strength(old) >= 2)
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for item in attachments:
            normalized = AttachmentMetadata.from_raw(item)
            key = normalized.source_url or f"{normalized.name}:{normalized.sha256}"
            if key not in seen:
                unique.append(item)
                seen.add(key)
        source_data = {**existing.source_data, **incoming.source_data, "attachments": unique,
                       "attachments_scanned": bool(existing.source_data.get("attachments_scanned") or
                                                   incoming.source_data.get("attachments_scanned"))}
        merged = incoming.model_copy(update={
            "name": existing.name,
            "source_data": source_data,
            "environment": incoming.environment or existing.environment,
            "connection_info": incoming.connection_info or existing.connection_info,
            "environment_required": incoming.environment_required or existing.environment_required,
        }).normalized()
        rows = {row["attachment_id"]: row for row in self.state.list_attachments(existing.native_id)}
        verified = []
        candidates = self._build_attachment_candidates(merged)
        current_ids = {candidate.attachment_id for candidate in candidates}
        for old_id, row in rows.items():
            if old_id not in current_ids and row.get("state") == "ready":
                self.state.invalidate_attachment(existing.native_id, old_id,
                                                 "attachment identity changed during registration")
        for candidate in candidates:
            row = rows.get(candidate.attachment_id, {})
            path = self._verified_saved_path(existing, candidate, row)
            if path is not None:
                verified.append(path.relative_to(self._directories[existing.name]).as_posix())
            elif row.get("state") == "ready":
                self._invalidate_saved(existing, candidate, row)
        if existing.state == ChallengeState.SOLVED:
            next_state = ChallengeState.SOLVED
        elif candidates and len(verified) == len(candidates):
            next_state = (ChallengeState.WAITING_FOR_ENVIRONMENT
                          if self._requires_environment(merged) and not self._has_environment_info(merged)
                          else ChallengeState.READY)
        elif existing.state in {ChallengeState.READY, ChallengeState.RUNNING}:
            next_state = ChallengeState.WAITING_FOR_PACKAGE
        else:
            next_state = existing.state
        return merged.model_copy(update={"files": sorted(set(verified)),
                                         "state": next_state,
                                         "reason": existing.reason if next_state == existing.state else ""}).normalized()

    def register_challenge(self, data: dict[str, Any]) -> ChallengeBundle:
        payload = dict(data)
        attachments = list(payload.get("attachments") or [])
        local_files: list[str] = []
        for index, item in enumerate(payload.get("files") or []):
            if isinstance(item, dict):
                attachments.append(item)
            elif isinstance(item, str) and item.replace("\\", "/").startswith("distfiles/"):
                local_files.append(item.replace("\\", "/"))
            elif isinstance(item, str):
                attachments.append(
                    {
                        "id": f"file-{index}",
                        "name": Path(item).name or f"attachment-{index}",
                        "source_url": item if item.startswith(("http://", "https://")) else "",
                    }
                )
        payload["files"] = local_files
        payload["mode"] = ChallengeMode.UNKNOWN
        environment_required = bool(
            payload.get("environment_required")
            or payload.get("requires_environment")
            or payload.get("connection_info")
            or payload.get("environment")
        )
        payload["environment_required"] = environment_required
        payload["source_data"] = {
            **dict(payload.get("source_data") or {}),
            "attachments": attachments,
            "environment_required": environment_required,
            "attachments_scanned": bool(payload.get("attachments_scanned")) or (
                bool(attachments)
                and all(
                    self._has_usable_attachment_metadata(item)
                    for item in attachments
                )
            ),
        }
        has_remote = bool(payload.get("connection_info") or payload.get("environment"))
        has_attachments = bool(local_files or attachments)
        is_solved = bool(payload.get("solved")) or str(
            payload.get("state") or payload.get("status") or ""
        ).casefold() == "solved"
        if is_solved:
            initial_state = ChallengeState.SOLVED
        elif has_attachments:
            # Attachment preparation must run even when the hybrid challenge's
            # environment has not been started yet.
            initial_state = ChallengeState.WAITING_FOR_DECISION
        else:
            initial_state = ChallengeState.READY if has_remote else (
                ChallengeState.WAITING_FOR_ENVIRONMENT
                if environment_required
                else ChallengeState.WAITING_FOR_DECISION
            )
        bundle = ChallengeBundle.model_validate(payload).model_copy(
            update={"state": initial_state}
        ).normalized()
        existing = next((known for known in self._bundles.values()
                         if known.native_id == bundle.native_id), None)
        if existing:
            if existing.name != bundle.name:
                raise ValueError(
                    f"Challenge ID {bundle.native_id!r} changed name from "
                    f"{existing.name!r} to {bundle.name!r}; registration refused"
                )
            bundle = self._merge_registered_bundle(existing, bundle)
        if bundle.state == ChallengeState.SOLVED:
            self._solved.add(bundle.name)
        return self._write_bundle(bundle)

    def _set_bundle_state(
        self, bundle: ChallengeBundle, state: ChallengeState, reason: str = ""
    ) -> ChallengeBundle:
        current = self._bundles.get(bundle.name)
        if current and current.native_id == bundle.native_id and current is not bundle:
            if current.state == ChallengeState.SOLVED and state != ChallengeState.SOLVED:
                return current
            bundle = current
        updated = bundle.model_copy(update={"state": state, "reason": reason}).normalized()
        return self._write_bundle(updated)

    def set_environment(self, challenge_name: str, data: dict[str, Any]) -> EnvironmentInfo:
        bundle = self._bundles.get(challenge_name)
        if not bundle:
            raise RuntimeError(f"Challenge is not registered: {challenge_name}")
        info = EnvironmentInfo.model_validate(data)
        if not (info.url or info.host or info.port is not None or info.metadata):
            raise RuntimeError("Environment data must include a URL, host, port, or metadata")
        if info.url:
            self.browser.allow_origin(info.url)
        updated = bundle.model_copy(update={
            "connection_info": info.url or bundle.connection_info,
            "environment_required": True,
            "environment": {**bundle.environment, **info.model_dump(exclude_none=True)},
            "mode": ChallengeMode.UNKNOWN,
            "reason": "",
        }).normalized()
        self._write_bundle(updated.model_copy(update={"state": self._readiness_state(updated)}))
        return info

    @staticmethod
    def _has_environment_info(bundle: ChallengeBundle) -> bool:
        return bool(bundle.connection_info or bundle.environment)

    @staticmethod
    def _requires_environment(bundle: ChallengeBundle) -> bool:
        return bool(
            bundle.environment_required
            or bundle.connection_info
            or bundle.environment
            or bundle.source_data.get("environment_required")
        )

    def _attachments_ready(self, bundle: ChallengeBundle) -> bool:
        candidates = self._build_attachment_candidates(bundle)
        if not candidates:
            return True
        rows = {
            item.get("attachment_id"): item
            for item in self.state.list_attachments(bundle.native_id)
        }
        for candidate in candidates:
            row = rows.get(candidate.attachment_id, {})
            if self._verified_saved_path(bundle, candidate, row) is None:
                self._invalidate_saved(bundle, candidate, row)
                return False
        return True

    def _readiness_state(self, bundle: ChallengeBundle) -> ChallengeState:
        has_attachments = bool(bundle.files or self._build_attachment_candidates(bundle))
        env_required = self._requires_environment(bundle)
        env_ready = self._has_environment_info(bundle)
        attachments_ready = self._attachments_ready(bundle)
        if env_required and not env_ready:
            return ChallengeState.WAITING_FOR_ENVIRONMENT
        if has_attachments and not attachments_ready:
            return ChallengeState.WAITING_FOR_PACKAGE
        if env_ready or attachments_ready and has_attachments:
            return ChallengeState.READY
        return ChallengeState.NEEDS_INPUT

    def _preparation_details(
        self,
        bundle: ChallengeBundle,
        candidates: list[AttachmentCandidate] | None = None,
    ) -> dict[str, Any]:
        candidates = candidates if candidates is not None else self._build_attachment_candidates(bundle)
        rows = {
            item.get("attachment_id"): item
            for item in self.state.list_attachments(bundle.native_id)
        }
        ready_count = sum(
            1
            for candidate in candidates
            if rows.get(candidate.attachment_id, {}).get("state") == "ready"
        )
        env_required = self._requires_environment(bundle)
        env_ready = self._has_environment_info(bundle)
        return {
            "mode": bundle.mode.value,
            "environment_required": env_required,
            "environment_ready": env_ready,
            "attachments_total": len(candidates),
            "attachments_ready": ready_count,
            "recommended_action": (
                "start_environment_and_call_set_environment"
                if env_required and not env_ready
                else "repair_attachment_metadata_or_retry"
                if candidates and ready_count < len(candidates)
                else "spawn_when_ready"
            ),
        }

    @staticmethod
    def _has_usable_attachment_metadata(item: Any) -> bool:
        if not isinstance(item, dict):
            return False
        metadata = AttachmentMetadata.from_raw(item)
        if metadata.target or metadata.challenge_page_url:
            return True
        return metadata.has_exact_source_url

    @staticmethod
    def _safe_filename(name: str) -> str:
        candidate = Path(str(name)).name.strip()
        if not candidate or candidate in {".", ".."}:
            raise ValueError("Attachment filename is empty")
        if re.search(r'[<>:"/\\|?*\x00-\x1f]', candidate):
            raise ValueError("Attachment filename contains unsafe characters")
        return candidate

    @staticmethod
    def _is_browser_evidence(path: Path) -> bool:
        return (
            path.name.startswith("page-") and path.suffix.lower() in {".yml", ".yaml"}
        ) or path.name.startswith("console-") or path.suffix.lower() in {
            ".json",
            ".jsonl",
            ".log",
            ".part",
            ".crdownload",
            ".tmp",
        }

    @staticmethod
    def _extract_snapshot_ref(text: str, attachment_name: str) -> str:
        """Extract the nearest Playwright ref from a snapshot/find response."""
        for line in text.splitlines():
            lowered = line.casefold()
            if attachment_name.casefold() in lowered and ("button" in lowered or "link" in lowered):
                exact = re.search(r"\[ref=([^\]]+)\]", line)
                if exact:
                    return exact.group(1)
        refs = re.findall(r"\[ref=([^\]]+)\]", text)
        if not refs:
            return ""
        name_index = text.casefold().find(attachment_name.casefold())
        if name_index < 0:
            return refs[-1]
        before = text[:name_index]
        nearby = re.findall(r"\[ref=([^\]]+)\]", before[-600:])
        after = re.findall(r"\[ref=([^\]]+)\]", text[name_index:name_index + 600])
        return (after or nearby or refs)[-1]

    @staticmethod
    def _derive_challenge_page(source_url: str) -> str:
        """Derive a visible challenge page from a CTF API attachment URL."""
        match = re.match(
            r"^(https?://[^/]+)/api/v1/competitions/([^/]+)/challenges/([^/]+)/attachments(?:/[^/?#]+)?",
            source_url,
        )
        if not match:
            return ""
        origin, competition_id, challenge_id = match.groups()
        return f"{origin}/competitions/{competition_id}/challenges?challenge={challenge_id}"

    async def _click_attachment_candidate(self, bundle: ChallengeBundle, candidate: AttachmentCandidate) -> str:
        """Click the UI attachment button, including platforms exposing API URLs."""
        target = candidate.target.strip()
        if target and not target.startswith(("http://", "https://", "/")):
            await self.browser.call("browser_snapshot", {})
            result = await self.browser.call("browser_click", {"target": target})
            if not str(result).startswith(("ERROR", "Playwright MCP error", "Browser tool")):
                return result
            found = await self.browser.call("browser_find", {"text": candidate.name})
            ref = self._extract_snapshot_ref(found, candidate.name)
            if ref:
                return await self.browser.call("browser_click", {"target": ref})
            return result

        page_url = self._derive_challenge_page(candidate.source_url) or str(
            (candidate.metadata or {}).get("challenge_page_url") or ""
        )
        if page_url:
            self.browser.allow_origin(page_url)
            await self.browser.call("browser_navigate", {"url": page_url})
            deadline = time.monotonic() + min(
                20, int(getattr(self.settings, "attachment_download_timeout_seconds", 60) or 60)
            )
            while time.monotonic() < deadline:
                snapshot = await self.browser.call("browser_snapshot", {})
                found = await self.browser.call("browser_find", {"text": candidate.name})
                ref = self._extract_snapshot_ref(found, candidate.name) or self._extract_snapshot_ref(
                    snapshot, candidate.name
                )
                if ref:
                    return await self.browser.call("browser_click", {"target": ref})
                await asyncio.sleep(0.5)
            return f"ERROR: attachment button not found for {candidate.name}"

        if candidate.source_url:
            return await self.browser.call("browser_navigate", {"url": candidate.source_url})
        return "ERROR: attachment has no usable browser target"

    def _infer_challenge_page(self, bundle: ChallengeBundle) -> str:
        if bundle.challenge_url:
            return bundle.challenge_url
        for known in self._bundles.values():
            for item in known.source_data.get("attachments") or []:
                if not isinstance(item, dict):
                    continue
                source_url = str(item.get("source_url") or item.get("url") or "")
                match = re.match(
                    r"^(https?://[^/]+)/api/v1/competitions/([^/]+)/challenges/",
                    source_url,
                )
                if match:
                    origin, competition_id = match.groups()
                    return (
                        f"{origin}/competitions/{competition_id}/challenges"
                        f"?challenge={bundle.native_id}"
                    )
        return ""

    @staticmethod
    def _platform_attachment_urls(bundle: ChallengeBundle) -> tuple[str, str]:
        match = re.match(
            r"^(https?://[^/]+)/competitions/([^/?#]+)/challenges/([^/?#]+)",
            bundle.challenge_url or "",
        )
        if not match or match.group(3) != str(bundle.native_id):
            return "", ""
        origin, competition_id, challenge_id = match.groups()
        return bundle.challenge_url, (
            f"{origin}/api/v1/competitions/{competition_id}/challenges/{challenge_id}/attachments"
        )

    @staticmethod
    def _browser_json_result(output: str) -> dict[str, Any]:
        # Playwright MCP prepends a human-readable result marker and code echo.
        match = re.search(r"(?:^|\n)### Result\s*\n(\{[^\n]*\})", output)
        if not match:
            return {}
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    async def _discover_authoritative_attachments(self, bundle: ChallengeBundle) -> ChallengeBundle:
        page_url, list_url = self._platform_attachment_urls(bundle)
        if (not list_url or "browser_run_code_unsafe" not in self.browser._tool_specs
            or self.browser._check_url(page_url) or self.browser._check_url(list_url)):
            return bundle
        # The request listener stays in the MCP process; its Bearer token is
        # never included in the tool result, model prompt, or Python state.
        code = f"""async (page) => {{
          const pageUrl = {json.dumps(page_url)};
          const listUrl = {json.dumps(list_url)};
          let auth;
          try {{
            const pending = page.waitForRequest(
              request => request.url().split('?')[0] === listUrl, {{timeout:12000}});
            await page.goto(pageUrl);
            const request = await pending;
            const headers = await request.allHeaders();
            auth = headers.authorization?.startsWith('Bearer ') ? headers.authorization : null;
          }} catch (_) {{ return {{ok:false, reason:'bearer_not_observed'}}; }}
          if (!auth) return {{ok:false, reason:'bearer_not_observed'}};
          const response = await page.request.get(listUrl, {{headers:{{Authorization:auth}}}});
          if (!response.ok()) return {{ok:false, reason:'list_http_' + response.status()}};
          const data = await response.json();
          return {{ok:true, items:Array.isArray(data.items) ? data.items.map(item => ({{
            id:item.id, fileName:item.fileName, byteLength:item.byteLength,
            sha256:item.sha256, challengeId:item.challengeId
          }})) : []}};
        }}"""
        async with self._browser_action_lock:
            result = self._browser_json_result(await self.browser.call("browser_run_code_unsafe", {"code": code}))
        if not result.get("ok"):
            reason = str(result.get("reason", "browser_tool_error"))
            logger.warning("Authoritative attachment discovery failed for %s: %s", bundle.name, reason)
            raise RuntimeError(f"attachment_metadata_unavailable: {reason}")
        original = bundle.source_data.get("attachments") or []
        indexed: dict[str, list[dict[str, Any]]] = {}
        for raw in original:
            normalized = AttachmentMetadata.from_raw(raw)
            indexed.setdefault(normalized.name, []).append(dict(raw) if isinstance(raw, dict) else {"name": normalized.name})
        authoritative = []
        for item in result.get("items", []):
            if not isinstance(item, dict) or not item.get("id") or not item.get("fileName"):
                continue
            try:
                declared_size = int(item.get("byteLength"))
            except (TypeError, ValueError):
                continue
            declared_hash = str(item.get("sha256") or "").lower()
            if declared_size <= 0 or not re.fullmatch(r"[0-9a-f]{64}", declared_hash):
                return bundle
            if item.get("challengeId") and str(item["challengeId"]) != bundle.native_id:
                logger.debug("Attachment list challengeId differs from page ID for %s", bundle.native_id)
            name = str(item["fileName"])
            matches = indexed.get(name, [])
            prior = matches.pop(0) if len(matches) == 1 else {}
            authoritative.append({
                **prior, "id": str(item["id"]), "fileName": name, "name": name,
                "byteLength": declared_size, "sha256": declared_hash,
                "source_url": f"{list_url}/{item['id']}", "challenge_page_url": page_url,
            })
        if not authoritative and (result.get("items") or bundle.source_data.get("attachments")):
            raise RuntimeError("attachment_metadata_unavailable: incomplete or missing authoritative records")
        updated = bundle.model_copy(update={"source_data": {
            **bundle.source_data, "attachments": authoritative, "attachments_scanned": True,
        }}).normalized()
        current_ids = {str(item["id"]) for item in authoritative}
        for row in self.state.list_attachments(bundle.native_id):
            if row["state"] == "ready" and row["attachment_id"] not in current_ids:
                self.state.invalidate_attachment(bundle.native_id, row["attachment_id"],
                                                 "authoritative attachment list changed")
        current = self._bundles.get(bundle.name)
        if current is not bundle and current and current.native_id == bundle.native_id:
            updated = self._merge_registered_bundle(current, updated)
        return self._write_bundle(updated)

    async def _discover_visible_attachment_candidates(
        self, bundle: ChallengeBundle
    ) -> ChallengeBundle:
        bundle = await self._discover_authoritative_attachments(bundle)
        attachments = bundle.source_data.get("attachments") or []
        # Metadata with a filename but no usable target still needs a page scan.
        metadata_complete = bool(attachments) and all(
            self._has_usable_attachment_metadata(item) for item in attachments
        )
        if bundle.source_data.get("attachments_scanned") and (
            metadata_complete or not attachments
        ):
            return bundle
        page_url = self._infer_challenge_page(bundle)
        if not page_url:
            logger.warning("Could not infer a challenge page for attachment scan: %s", bundle.name)
            async with self._browser_action_lock:
                snapshot = await self.browser.call("browser_snapshot", {})
            if bundle.name.casefold() not in snapshot.casefold() or "附件" not in snapshot:
                return bundle
        else:
            self.browser.allow_origin(page_url)
            snapshot = ""
            async with self._browser_action_lock:
                await self.browser.call("browser_navigate", {"url": page_url})
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    snapshot = await self.browser.call("browser_snapshot", {})
                    if bundle.name.casefold() in snapshot.casefold() and "附件" in snapshot:
                        break
                    await asyncio.sleep(0.5)
        # Sidebar entries may contain every challenge name. Only the active
        # detail heading proves that the attachment buttons belong to this one.
        detail_titles = re.findall(r'- heading "([^"]+)" \[level=2\]', snapshot)
        if bundle.name.casefold() not in {title.casefold() for title in detail_titles}:
            raise RuntimeError("attachment_page_mismatch: active challenge heading does not match")
        snapshot_lines = snapshot.splitlines()
        attachment_lines: list[str] = []
        heading_indent: int | None = None
        for line in snapshot_lines:
            if heading_indent is None:
                if 'heading "附件"' in line:
                    heading_indent = len(line) - len(line.lstrip())
                continue
            indent = len(line) - len(line.lstrip())
            if indent < heading_indent and line.lstrip().startswith("- region"):
                break
            attachment_lines.append(line)
        attachment_section = "\n".join(attachment_lines)
        # A UI snapshot only supplies a button target. It is not authoritative
        # for attachment identity, size, digest, or exact API URL.
        existing_by_name: dict[str, list[dict[str, Any]]] = {}
        for item in attachments:
            normalized = AttachmentMetadata.from_raw(item)
            existing_by_name.setdefault(normalized.name, []).append(
                dict(item) if isinstance(item, dict) else {"name": normalized.name, "source_url": normalized.source_url}
            )
        discovered: list[dict[str, Any]] = []
        for name, _ref in re.findall(r'- button "([^"]+)" \[ref=([^\]]+)\]', attachment_section):
            matches = existing_by_name.get(name, [])
            # A button supplies a locator, never attachment identity/content.
            # Unknown or duplicate names must not create a downloadable item.
            if len(matches) != 1:
                continue
            prior = matches.pop()
            discovered.append({
                **prior,
                "fileName": name,
                "name": name,
                **({"challenge_page_url": page_url} if page_url else {}),
                **({"target": _ref} if not page_url else {}),
            })
        # Keep authoritative API metadata even if its button was not visible.
        discovered.extend(item for remaining in existing_by_name.values() for item in remaining)
        if not discovered and re.search(r'- button "[^"]+" \[ref=[^\]]+\]', attachment_section):
            raise RuntimeError("attachment_metadata_unavailable: visible buttons have no verified identity")
        updated = bundle.model_copy(
            update={
                "source_data": {
                    **bundle.source_data,
                    "attachments": discovered,
                    "attachments_scanned": True,
                }
            }
        ).normalized()
        current = self._bundles.get(bundle.name)
        if current is not bundle and current and current.native_id == bundle.native_id:
            updated = self._merge_registered_bundle(current, updated)
        return self._write_bundle(updated)

    async def _browser_fetch_attachment(
        self, bundle: ChallengeBundle, candidate: AttachmentCandidate, staged_name: str,
    ) -> str:
        """Fetch with a short-lived in-MCP Bearer, never returning the credential."""
        page_url, list_url = self._platform_attachment_urls(bundle)
        if not list_url:
            # Other supported platforms may authorize downloads with cookies.
            # The verified NoCTF route below never falls back to cookie-only fetch.
            function = f"""async () => {{
              const response = await fetch({json.dumps(candidate.source_url)}, {{credentials: 'include'}});
              if (!response.ok) throw new Error('download_http_' + response.status);
              const blob = await response.blob();
              const filename = {json.dumps(staged_name)};
              const url = URL.createObjectURL(blob);
              const anchor = document.createElement('a');
              anchor.href=url; anchor.download=filename;
              document.body.appendChild(anchor); anchor.click(); anchor.remove();
              setTimeout(() => URL.revokeObjectURL(url), 60000);
              return {{ok:true, bytes:blob.size}};
            }}"""
            return await self.browser.call("browser_run_code_unsafe", {
                "code": f"async (page) => await page.evaluate({function})",
            })
        if not self._exact_url_matches(bundle, candidate):
            return "ERROR: attachment URL is not bound to this challenge"
        if (self.browser._check_url(page_url) or self.browser._check_url(list_url)
            or self.browser._check_url(candidate.source_url)):
            return "ERROR: attachment origin is not allowed"
        staged_path = (self.browser.download_dir / staged_name).resolve()
        if self.browser.download_dir.resolve() not in staged_path.parents:
            return "ERROR: attachment staging path escaped download directory"
        expected_size, expected_hash = self._expected_attachment(candidate)
        if expected_size is None or not expected_hash:
            return "ERROR: attachment size and SHA-256 are required"
        if expected_size > MAX_AUTH_TRANSFER_BYTES:
            return "ERROR: attachment_exceeds_mcp_transfer_limit"
        code = f"""async (page) => {{
          const pageUrl = {json.dumps(page_url)};
          const listUrl = {json.dumps(list_url)};
          const fileUrl = {json.dumps(candidate.source_url)};
          async function getBearer() {{
            try {{
              const pending = page.waitForRequest(
                request => request.url().split('?')[0] === listUrl, {{timeout:12000}});
              await page.goto(pageUrl);
              const request = await pending;
              const headers = await request.allHeaders();
              return headers.authorization?.startsWith('Bearer ') ? headers.authorization : null;
            }} catch (_) {{ return null; }}
          }}
          let response;
          for (let attempt=0; attempt<2; ++attempt) {{
            const bearer = await getBearer();
            if (!bearer) return {{ok:false, reason:'bearer_not_observed'}};
            response = await page.request.get(fileUrl, {{headers:{{Authorization:bearer}}}});
            if (response.status() !== 401) break;
          }}
          if (!response.ok()) return {{ok:false, reason:'download_http_' + response.status()}};
          const contentType = (response.headers()['content-type'] || '').toLowerCase();
          if (contentType.includes('application/json') || contentType.includes('text/html'))
            return {{ok:false, reason:'unexpected_content_type'}};
          const advertisedLength = Number(response.headers()['content-length'] || 0);
          if (advertisedLength > {MAX_AUTH_TRANSFER_BYTES})
            return {{ok:false, reason:'attachment_exceeds_mcp_transfer_limit'}};
          const bytes = await response.body();
          if (bytes.length > {MAX_AUTH_TRANSFER_BYTES})
            return {{ok:false, reason:'attachment_exceeds_mcp_transfer_limit'}};
          if (bytes.length !== {expected_size})
            return {{ok:false, reason:'download_size_mismatch'}};
          return {{ok:true, bytes:bytes.length, payload:bytes.toString('base64')}};
        }}"""
        output = await self.browser.call("browser_run_code_unsafe", {"code": code})
        result = self._browser_json_result(output)
        if not result.get("ok"):
            return f"ERROR: authenticated_attachment_{result.get('reason', 'browser_failure')}"
        try:
            encoded = result["payload"]
            if not isinstance(encoded, str) or len(encoded) > ((expected_size + 2) // 3) * 4:
                return "ERROR: authenticated_attachment_invalid_payload"
            payload = base64.b64decode(encoded, validate=True)
        except (KeyError, ValueError, binascii.Error):
            return "ERROR: authenticated_attachment_invalid_payload"
        if len(payload) != expected_size:
            return "ERROR: download_hash_mismatch: attachment byte count differs from metadata"
        if hashlib.sha256(payload).hexdigest().casefold() != expected_hash:
            return "ERROR: download_hash_mismatch: SHA-256 differs from metadata"
        # Do not persist rejected bytes. The archive step copies from this
        # unique staging path and performs its own independent integrity check.
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        with staged_path.open("xb") as stream:
            stream.write(payload)
        return "ok"

    @staticmethod
    def _is_exact_attachment_url(source_url: str) -> bool:
        return bool(re.search(r"/attachments/[^/?#]+(?:[?#].*)?$", source_url or "", re.IGNORECASE))

    @staticmethod
    def _expected_attachment(candidate: AttachmentCandidate) -> tuple[int | None, str]:
        metadata = candidate.metadata or {}
        raw_size = candidate.size if candidate.size is not None else metadata.get(
            "byte_length", metadata.get("byteLength", metadata.get("size"))
        )
        try:
            size = int(raw_size) if raw_size is not None else None
        except (TypeError, ValueError):
            size = None
        sha256 = str(metadata.get("sha256") or "").strip().casefold()
        return size, sha256

    @staticmethod
    def _exact_url_matches(bundle: ChallengeBundle, candidate: AttachmentCandidate) -> bool:
        match = re.search(r"/challenges/([^/?#]+)/attachments/([^/?#]+)(?:[?#].*)?$",
                          candidate.source_url or "", re.IGNORECASE)
        return bool(match and match.group(1) == str(bundle.native_id)
                    and match.group(2) == str(candidate.attachment_id))

    def _verified_saved_path(self, bundle: ChallengeBundle, candidate: AttachmentCandidate,
                             row: dict[str, Any]) -> Path | None:
        relative = str(row.get("relative_path") or "")
        directory = self._directories.get(bundle.name)
        if row.get("state") != "ready" or not directory or not relative:
            return None
        path = (directory / relative).resolve()
        if (directory / "distfiles").resolve() not in path.parents or not path.is_file():
            return None
        digest, size = self.state.sha256_file(path)
        expected_size, expected_hash = self._expected_attachment(candidate)
        if (not expected_hash and row.get("reason") != "verified exact attachment URL"):
            return None
        if (not row.get("sha256") or digest.casefold() != str(row["sha256"]).casefold()
            or row.get("bytes") is None or size != int(row["bytes"])
            or (expected_size is not None and size != expected_size)
            or (expected_hash and digest.casefold() != expected_hash)):
            return None
        return path

    def _invalidate_saved(self, bundle: ChallengeBundle, candidate: AttachmentCandidate,
                          row: dict[str, Any]) -> None:
        if row.get("state") != "ready":
            return
        self.state.invalidate_attachment(bundle.native_id, candidate.attachment_id,
                                         "saved attachment failed integrity check")
        relative = str(row.get("relative_path") or "")
        if relative and relative in bundle.files:
            self._write_bundle(bundle.model_copy(update={
                "files": [f for f in bundle.files if f != relative]}))

    async def _claim_download(
        self,
        paths: list[Path],
        candidate: AttachmentCandidate,
        expected_name: str,
    ) -> Path | None:
        expected_size, expected_sha256 = self._expected_attachment(candidate)
        ordered = sorted(paths, key=lambda path: (path.name != expected_name, path.name))
        async with self._download_claim_lock:
            for path in ordered:
                resolved = path.resolve()
                if resolved in self._claimed_downloads or not path.is_file():
                    continue
                if path.name != expected_name and not expected_sha256:
                    continue
                if expected_size is not None and path.stat().st_size != expected_size:
                    continue
                if expected_sha256:
                    digest, _ = self.state.sha256_file(path)
                    if digest.casefold() != expected_sha256:
                        continue
                self._claimed_downloads.add(resolved)
                return path
        return None

    def _build_attachment_candidates(self, bundle: ChallengeBundle) -> list[AttachmentCandidate]:
        raw = bundle.source_data.get("attachments") or bundle.source_data.get("files") or []
        candidates: list[AttachmentCandidate] = []
        for index, item in enumerate(raw):
            normalized = AttachmentMetadata.from_raw(item, index)
            metadata = dict(normalized.raw or {})
            metadata.update(
                {
                    "id": normalized.attachment_id,
                    "file_name": normalized.name,
                    "source_url": normalized.source_url,
                }
            )
            if normalized.size is not None:
                metadata["byte_length"] = normalized.size
            if normalized.sha256:
                metadata["sha256"] = normalized.sha256
            if normalized.challenge_page_url:
                metadata["challenge_page_url"] = normalized.challenge_page_url
            candidates.append(
                AttachmentCandidate(
                    attachment_id=normalized.attachment_id,
                    name=normalized.name,
                    target=normalized.target,
                    source_url=normalized.source_url,
                    size=normalized.size,
                    metadata=metadata,
                )
            )
        return candidates

    def _migrate_existing_artifacts(
        self,
        bundle: ChallengeBundle,
        candidates: list[AttachmentCandidate],
    ) -> ChallengeBundle:
        """Recognize already downloaded, verified distfiles after restart/manual download."""
        directory = self._directories.get(bundle.name)
        if not directory:
            return bundle
        distfiles = directory / "distfiles"
        if not distfiles.is_dir():
            return bundle
        files = set(bundle.files)
        changed = False
        for candidate in candidates:
            try:
                expected_name = self._safe_filename(candidate.name)
            except ValueError:
                continue
            path = (distfiles / expected_name).resolve()
            if distfiles.resolve() not in path.parents or not path.is_file():
                continue
            expected_size, expected_sha256 = self._expected_attachment(candidate)
            byte_count = path.stat().st_size
            if byte_count <= 0 or not expected_sha256 or (expected_size is not None and byte_count != expected_size):
                continue
            digest, byte_count = self.state.sha256_file(path)
            if expected_sha256 and digest.casefold() != expected_sha256:
                continue
            relative = path.relative_to(directory).as_posix()
            self.state.upsert_attachment(bundle.native_id, candidate)
            self.state.set_attachment_state(
                bundle.native_id,
                candidate.attachment_id,
                "ready",
                relative_path=relative,
                sha256=digest,
                byte_count=byte_count,
                reason="recovered existing verified distfile",
            )
            if relative not in files:
                files.add(relative)
                changed = True
        rows = self.state.list_attachments(bundle.native_id)
        all_ready = bool(candidates) and all(
            any(
                row.get("attachment_id") == candidate.attachment_id
                and self._verified_saved_path(bundle, candidate, row) is not None
                for row in rows
            )
            for candidate in candidates
        )
        if changed or (all_ready and bundle.state not in {ChallengeState.READY, ChallengeState.SOLVED}):
            updated = bundle.model_copy(
                update={
                    "files": sorted(files),
                    "reason": "",
                }
            ).normalized()
            final_state = self._readiness_state(updated) if all_ready else updated.state
            return self._write_bundle(updated.model_copy(update={"state": final_state}))
        return bundle

    async def list_attachment_candidates(self, challenge_id: str) -> list[AttachmentCandidate]:
        bundle = await self.prepare_challenge(challenge_id)
        candidates = self._build_attachment_candidates(bundle)
        for candidate in candidates:
            self.state.upsert_attachment(bundle.native_id, candidate)
        self._migrate_existing_artifacts(bundle, candidates)
        return candidates

    async def _wait_for_download(
        self,
        before: dict[str, int],
        candidate: AttachmentCandidate,
        expected_name: str,
        timeout: int,
    ) -> Path | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            files = [path for path in self.browser.download_dir.iterdir() if path.is_file()]
            new_files = [
                path
                for path in files
                if (
                    path.name not in before
                    or path.stat().st_mtime_ns != before[path.name]
                )
                and not self._is_browser_evidence(path)
            ]
            stable_files: list[Path] = []
            for candidate_source in new_files:
                initial_size = candidate_source.stat().st_size
                await asyncio.sleep(0.25)
                if candidate_source.exists() and candidate_source.stat().st_size == initial_size:
                    stable_files.append(candidate_source)
            source = await self._claim_download(stable_files, candidate, expected_name)
            if source is not None:
                return source
            await asyncio.sleep(0.25)
        return None

    async def _archive_downloaded_attachment(
        self,
        bundle: ChallengeBundle,
        candidate: AttachmentCandidate,
        source: Path,
    ) -> AttachmentArtifact:
        source = source.resolve()
        download_dir = self.browser.download_dir.resolve()
        if download_dir not in source.parents:
            raise RuntimeError("download_artifact_outside_staging: download is outside the configured staging directory")
        filename = self._safe_filename(candidate.name)
        digest, byte_count = self.state.sha256_file(source)
        expected_size, expected_sha256 = self._expected_attachment(candidate)
        if byte_count <= 0:
            raise RuntimeError("download_artifact_invalid: downloaded attachment is empty")
        if expected_size is not None and byte_count != expected_size:
            raise RuntimeError(
                f"download_hash_mismatch: expected {expected_size} bytes, got {byte_count}"
            )
        if expected_sha256 and digest.casefold() != expected_sha256:
            raise RuntimeError("download_hash_mismatch: SHA-256 does not match attachment metadata")
        current = self._bundles.get(bundle.name, bundle)
        latest_candidate = next((item for item in self._build_attachment_candidates(current)
                                 if item.attachment_id == candidate.attachment_id), None)
        if (latest_candidate is None or self._expected_attachment(latest_candidate) !=
            self._expected_attachment(candidate)):
            raise RuntimeError("attachment_identity_changed: registration replaced this attachment")
        bundle = current
        destination_dir = self._directories[bundle.name] / "distfiles"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = (destination_dir / filename).resolve()
        if destination_dir.resolve() not in destination.parents:
            raise RuntimeError("download_artifact_invalid_filename: invalid download filename")
        if destination.is_file() and self.state.sha256_file(destination)[0] != digest:
            quarantine = (self.state.path.parent / "attachment-conflicts" / self.state.run_id
                          / self._slug(bundle.name) / f"{uuid.uuid4().hex}-{filename}")
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, quarantine)
        temporary = destination.with_suffix(destination.suffix + ".part")
        shutil.copy2(source, temporary)
        temporary.replace(destination)
        relative = destination.relative_to(self._directories[bundle.name]).as_posix()
        self.state.set_attachment_state(
            bundle.native_id,
            candidate.attachment_id,
            "ready",
            relative_path=relative,
            sha256=digest,
            byte_count=byte_count,
            reason="verified exact attachment URL" if self._exact_url_matches(bundle, candidate)
                   else "verified platform SHA-256",
        )
        updated = bundle.model_copy(update={
            "files": sorted(set(bundle.files + [relative])),
            "reason": "",
        }).normalized()
        self._write_bundle(updated.model_copy(update={"state": self._readiness_state(updated)}))
        return AttachmentArtifact(candidate.attachment_id, filename, relative, digest, byte_count)

    async def download_attachment(self, challenge_id: str, attachment_id: str) -> AttachmentArtifact:
        bundle = self._bundles.get(challenge_id)
        if not bundle:
            bundle = await self.prepare_challenge(challenge_id)
        candidates = await self.list_attachment_candidates(bundle.native_id)
        candidate = next((item for item in candidates if item.attachment_id == str(attachment_id)), None)
        if not candidate:
            raise KeyError(f"Attachment {attachment_id!r} is not registered for {challenge_id!r}")
        saved = next(
            (
                item
                for item in self.state.list_attachments(bundle.native_id)
                if item.get("attachment_id") == candidate.attachment_id
            ),
            {},
        )
        saved_path = self._verified_saved_path(bundle, candidate, saved)
        if saved_path is not None:
            digest, byte_count = self.state.sha256_file(saved_path)
            return AttachmentArtifact(candidate.attachment_id, saved_path.name,
                                      saved_path.relative_to(self._directories[bundle.name]).as_posix(),
                                      digest, byte_count)
        self._invalidate_saved(bundle, candidate, saved)

        timeout = int(getattr(self.settings, "attachment_download_timeout_seconds", 60) or 60)
        max_attempts = max(1, int(getattr(self.settings, "attachment_max_retries", 3) or 3))
        expected_name = self._safe_filename(candidate.name)
        last_error = "download failed"
        has_exact_url = self._is_exact_attachment_url(candidate.source_url)
        if has_exact_url and not self._exact_url_matches(bundle, candidate):
            raise RuntimeError("attachment_identity_mismatch: URL IDs do not match candidate")
        if self._platform_attachment_urls(bundle)[1] and has_exact_url:
            size, sha = self._expected_attachment(candidate)
            if size is None or size <= 0 or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise RuntimeError("attachment_unverifiable: platform size and SHA-256 are required")
        metadata = candidate.metadata or {}
        has_ui_route = bool(candidate.target or metadata.get("challenge_page_url"))
        if not has_ui_route and not has_exact_url:
            reason = (
                "attachment_exact_url_missing: attachment has no usable button target "
                "or exact authenticated download URL"
            )
            self.state.set_attachment_state(
                bundle.native_id,
                candidate.attachment_id,
                "failed",
                reason=reason,
            )
            self._set_bundle_state(bundle, ChallengeState.NEEDS_INPUT, reason)
            raise RuntimeError(reason)

        self.browser.download_dir.mkdir(parents=True, exist_ok=True)

        for attempt in range(max_attempts):
            try:
                self.state.set_attachment_state(
                    bundle.native_id,
                    candidate.attachment_id,
                    "downloading",
                    increment_attempts=True,
                )
                before = {
                    path.name: path.stat().st_mtime_ns
                    for path in self.browser.download_dir.iterdir()
                    if path.is_file()
                }
                source: Path | None = None
                authenticated_staged = False
                ui_error = ""
                # The action and collection are atomic with respect to other workers.
                async with self._browser_action_lock:
                    if has_exact_url and "browser_run_code_unsafe" in self.browser._tool_specs:
                        staged_name = f"{candidate.attachment_id}-{uuid.uuid4().hex}.download"
                        fetch_result = await self._browser_fetch_attachment(bundle, candidate, staged_name)
                        if str(fetch_result).startswith(("ERROR", "Playwright MCP error", "Browser tool")):
                            raise RuntimeError(str(fetch_result))
                        staged_path = self.browser.download_dir / staged_name
                        if not staged_path.is_file():
                            raise FileNotFoundError("download_artifact_not_found: authenticated staging file missing")
                        source = staged_path
                        authenticated_staged = bool(self._platform_attachment_urls(bundle)[1])
                    elif has_ui_route:
                        if not self._expected_attachment(candidate)[1]:
                            raise RuntimeError("attachment_unverifiable: UI-only download requires SHA-256")
                        ui_result = await self._click_attachment_candidate(bundle, candidate)
                        ui_error = str(ui_result)
                        source = await self._wait_for_download(before, candidate, expected_name, timeout)
                    else:
                        raise RuntimeError("browser_fetch_unavailable: exact URL needs authenticated fetch")
                if source is None:
                    if has_ui_route and ui_error:
                        raise FileNotFoundError(
                            f"download_artifact_not_found: {ui_error}; no matching browser download"
                        )
                    if not has_ui_route and not has_exact_url:
                        raise RuntimeError(
                            "attachment_exact_url_missing: attachment has no usable button target or exact download URL"
                        )
                    raise FileNotFoundError(
                        "download_artifact_not_found: no browser download matched name/size/SHA-256"
                    )

                try:
                    return await self._archive_downloaded_attachment(bundle, candidate, source)
                finally:
                    if authenticated_staged:
                        source.unlink(missing_ok=True)
            except Exception as exc:
                last_error = str(exc)
                self.state.set_attachment_state(
                    bundle.native_id,
                    candidate.attachment_id,
                    "failed",
                    reason=last_error[:500],
                )
                # Retrying a proven 404, corrupt body, or transport size limit
                # cannot repair this attachment and needlessly delays the user.
                if any(marker in last_error for marker in (
                    "download_http_404", "download_hash_mismatch", "download_size_mismatch",
                    "attachment_exceeds_mcp_transfer_limit", "download_http_401",
                    "attachment_unverifiable",
                )):
                    break
                if attempt + 1 < max_attempts:
                    await asyncio.sleep((2, 5, 15)[min(attempt, 2)])

        reason = f"Attachment download failed after {max_attempts} attempts: {last_error}"
        self._set_bundle_state(bundle, ChallengeState.NEEDS_INPUT, reason[:2000])
        raise RuntimeError(reason)

    async def prepare_challenge_package(self, challenge_id: str) -> dict[str, Any]:
        """Prepare every registered attachment and make the challenge solver-ready."""
        bundle = await self.prepare_challenge(challenge_id)
        if bundle.state == ChallengeState.SOLVED:
            return {"state": "solved", "message": "challenge is already solved"}
        bundle = self._set_bundle_state(bundle, ChallengeState.PREPARING)
        try:
            bundle = await self._discover_visible_attachment_candidates(bundle)
        except Exception as exc:
            reason = str(exc)[:500]
            self._set_bundle_state(bundle, ChallengeState.NEEDS_INPUT, reason)
            return {"state": "needs_input", "message": reason,
                    "details": self._preparation_details(bundle)}
        candidates = await self.list_attachment_candidates(bundle.name)
        if not candidates:
            if self._requires_environment(bundle) and not self._has_environment_info(bundle):
                self._set_bundle_state(
                    bundle,
                    ChallengeState.WAITING_FOR_ENVIRONMENT,
                    "Environment is required but has not been started or registered",
                )
                return {
                    "state": ChallengeState.WAITING_FOR_ENVIRONMENT.value,
                    "message": "environment required; start it in the browser and call set_environment",
                    "details": self._preparation_details(bundle, candidates),
                }
            if self._has_environment_info(bundle):
                self._set_bundle_state(bundle, ChallengeState.READY)
                return {
                    "state": "ready",
                    "message": "remote challenge is ready",
                    "details": self._preparation_details(bundle, candidates),
                }
            reason = "Challenge has neither registered attachments nor a remote environment"
            self._set_bundle_state(bundle, ChallengeState.NEEDS_INPUT, reason)
            return {
                "state": "needs_input",
                "message": reason,
                "details": self._preparation_details(bundle, candidates),
            }

        bundle = self._set_bundle_state(bundle, ChallengeState.WAITING_FOR_PACKAGE)
        existing = {
            item["attachment_id"]: item
            for item in self.state.list_attachments(bundle.native_id)
        }
        completed: list[str] = []
        try:
            for candidate in candidates:
                saved = existing.get(candidate.attachment_id, {})
                if self._verified_saved_path(bundle, candidate, saved) is not None:
                    completed.append(candidate.name)
                    continue
                self._invalidate_saved(bundle, candidate, saved)
                await self.download_attachment(bundle.name, candidate.attachment_id)
                completed.append(candidate.name)
        except Exception as exc:
            evidence = sorted(
                self.browser.download_dir.glob("page-*.yml"),
                key=lambda path: path.stat().st_mtime_ns,
                reverse=True,
            )
            evidence_path = str(evidence[0]) if evidence else ""
            reason = (
                f"Attachment preparation failed: {exc}; completed={completed}; "
                f"evidence={evidence_path or 'unavailable'}"
            )
            self._set_bundle_state(bundle, ChallengeState.NEEDS_INPUT, reason[:2000])
            return {
                "state": "needs_input",
                "message": reason,
                "details": self._preparation_details(bundle, candidates),
            }

        refreshed = await self.prepare_challenge(bundle.name)
        final_state = self._readiness_state(refreshed)
        reason = (
            "Environment is required but has not been started or registered"
            if final_state == ChallengeState.WAITING_FOR_ENVIRONMENT
            else ""
        )
        self._set_bundle_state(refreshed, final_state, reason)
        return {
            "state": final_state.value,
            "message": (
                f"prepared {len(completed)} attachment(s); environment still required"
                if final_state == ChallengeState.WAITING_FOR_ENVIRONMENT
                else f"prepared {len(completed)} attachment(s)"
            ),
            "details": self._preparation_details(refreshed, candidates),
        }

    async def mark_challenge_solved(self, challenge_id: str) -> None:
        bundle = await self.prepare_challenge(challenge_id)
        self._solved.add(bundle.name)
        self._set_bundle_state(bundle, ChallengeState.SOLVED)

    async def import_latest_download(self, challenge_name: str, filename: str = "") -> dict[str, Any]:
        """Import an explicitly named file already downloaded by the browser."""
        if not filename:
            raise RuntimeError("Explicit attachment filename is required")
        bundle = await self.prepare_challenge(challenge_name)
        candidates = await self.list_attachment_candidates(challenge_name)
        candidate = next((item for item in candidates if Path(item.name).name == Path(filename).name), None)
        if not candidate:
            raise RuntimeError(f"Attachment {filename!r} is not registered")
        expected_name = self._safe_filename(candidate.name)
        if not self._expected_attachment(candidate)[1]:
            raise RuntimeError("attachment_unverifiable: staged file requires SHA-256")
        self.browser.download_dir.mkdir(parents=True, exist_ok=True)
        paths = [
            path
            for path in self.browser.download_dir.iterdir()
            if path.is_file() and path.name == expected_name and not self._is_browser_evidence(path)
        ]
        source = await self._claim_download(paths, candidate, expected_name)
        if source is None:
            raise RuntimeError(
                f"download_artifact_not_found: no staged browser download named {expected_name!r}"
            )
        artifact = await self._archive_downloaded_attachment(bundle, candidate, source)
        result = artifact.as_dict()
        result["path"] = artifact.relative_path
        return result

    async def prepare_challenge(self, challenge_id: str) -> ChallengeBundle:
        if challenge_id not in self._bundles:
            await self.list_challenges()
        bundle = next((item for item in self._bundles.values() if item.name == challenge_id or item.native_id == str(challenge_id)), None)
        if not bundle:
            raise RuntimeError(f"Challenge is not registered: {challenge_id}")
        return bundle

    async def start_environment(self, challenge_id: str) -> EnvironmentInfo:
        bundle = await self.prepare_challenge(challenge_id)
        if bundle.environment.get("source") in {"compose", "docker-compose"}:
            env = {**bundle.environment, "challenge_dir": self._slug(bundle.name)}
            return await self._environments.start(bundle.name, env)
        if bundle.connection_info:
            self.browser.allow_origin(bundle.connection_info)
            return EnvironmentInfo(status="ready", source="remote", url=bundle.connection_info)
        raise RuntimeError("No environment information is registered; use Playwright to start it and set_environment")

    async def get_solve_status(self) -> set[str]:
        return set(self._solved)

    def get_confirmed_flag(self, challenge_id: str) -> str | None:
        bundle = next(
            (item for item in self._bundles.values()
             if item.name == challenge_id or item.native_id == challenge_id),
            None,
        )
        aliases = {challenge_id}
        if bundle:
            aliases.update({bundle.name, bundle.native_id})
        for confirmation in reversed(self._submission_confirmations):
            if confirmation.accepted and confirmation.challenge_id in aliases:
                return confirmation.flag
        return None

    async def get_challenge_state(self, challenge_id: str) -> dict[str, Any]:
        bundle = await self.prepare_challenge(challenge_id)
        if bundle.state != ChallengeState.SOLVED and self._build_attachment_candidates(bundle):
            verified_state = self._readiness_state(bundle)
            if bundle.state == ChallengeState.READY and verified_state != ChallengeState.READY:
                bundle = self._set_bundle_state(bundle, verified_state, "saved attachment failed integrity check")
        state = self.state.get_challenge(bundle.native_id) or {}
        state["attachments"] = self.state.list_attachments(bundle.native_id)
        return state

    async def mark_needs_input(self, challenge_id: str, reason: str) -> str:
        bundle = await self.prepare_challenge(challenge_id)
        self.state.set_challenge_state(bundle.native_id, "needs_input", reason)
        updated = bundle.model_copy(
            update={"state": ChallengeState.NEEDS_INPUT, "reason": reason}
        ).normalized()
        self._write_bundle(updated)
        return f"{challenge_id}: needs_input — {reason}"

    async def retry_challenge_preparation(self, challenge_id: str) -> str:
        bundle = await self.prepare_challenge(challenge_id)
        self.state.retry_challenge(bundle.native_id)
        updated = bundle.model_copy(
            update={"state": ChallengeState.WAITING_FOR_DECISION, "reason": ""}
        ).normalized()
        self._write_bundle(updated)
        return f"{challenge_id}: preparation reset; attachment candidates can be retried"

    async def submit_flag(self, challenge_id: str, flag: str) -> SubmissionResult:
        if not self.allow_submit:
            return SubmissionResult(status="dry_run", display=f'DRY RUN — would submit "{flag.strip()}" for {challenge_id}')
        recipe = self.recipes.load(self.base_url)
        issue = submission_recipe_issue(recipe, self.base_url)
        if issue:
            raise RuntimeError(f"{issue}; use the Coordinator to discover and save one")
        assert recipe is not None
        bundle = next(
            (item for item in self._bundles.values()
             if item.name == challenge_id or item.native_id == challenge_id),
            None,
        )
        route_id = bundle.native_id if bundle else challenge_id
        async with self._browser_action_lock:
            await self._execute_recipe(recipe, challenge_id=route_id, flag=flag, purpose="submit")
            snapshot = await self._checked_recipe_browser_call("browser_snapshot", {})
        lowered = snapshot.casefold()
        success = [marker for marker in recipe.success_markers if marker.casefold() in lowered]
        failure = [marker for marker in recipe.failure_markers if marker.casefold() in lowered]
        normalized = flag.strip()
        self._pending_submissions[challenge_id] = PendingSubmission(
            flag=normalized,
            submitted_at=time.time(),
            initial_evidence=snapshot,
        )
        return SubmissionResult(
            status="pending",
            message="Submission performed; Agent must judge the browser evidence",
            display=(
                "SUBMISSION_PENDING — inspect this Playwright page evidence and call "
                f"confirm_submission. success_markers={success!r}, failure_markers={failure!r}: "
                f"{snapshot[:12000]}"
            ),
        )

    async def confirm_submission(
        self, challenge_id: str, flag: str, accepted: bool, reason: str
    ) -> SubmissionResult:
        pending = self._pending_submissions.get(challenge_id)
        normalized = flag.strip()
        reason = reason.strip()
        if pending is None:
            raise RuntimeError(f"No pending submission for {challenge_id!r}")
        if normalized != pending.flag:
            raise RuntimeError("Confirmation flag does not match the pending submission")
        if not reason:
            raise RuntimeError("Submission confirmation requires a non-empty reason")

        recipe = self.recipes.load(self.base_url)
        if not recipe:
            raise RuntimeError("No submit recipe is available for confirmation")
        async with self._browser_action_lock:
            snapshot = await self._checked_recipe_browser_call("browser_snapshot", {})
        lowered = snapshot.casefold()
        success = tuple(marker for marker in recipe.success_markers if marker.casefold() in lowered)
        failure = tuple(marker for marker in recipe.failure_markers if marker.casefold() in lowered)
        conflicting = failure if accepted else success
        if conflicting and not any(marker.casefold() in reason.casefold() for marker in conflicting):
            raise RuntimeError(
                "Agent override reason must explicitly mention the conflicting marker: "
                + ", ".join(conflicting)
            )

        self._submission_confirmations.append(
            SubmissionConfirmation(
                challenge_id=challenge_id,
                flag=normalized,
                accepted=accepted,
                reason=reason,
                evidence=snapshot,
                success_markers=success,
                failure_markers=failure,
                confirmed_at=time.time(),
            )
        )
        del self._pending_submissions[challenge_id]
        if not accepted:
            return SubmissionResult(
                status="incorrect",
                message=reason,
                display=f'INCORRECT — Agent rejected "{normalized}": {reason}',
            )
        self._solved.add(challenge_id)
        return SubmissionResult(
            status="correct",
            message=reason,
            display=f'CORRECT — Agent confirmed "{normalized}": {reason}',
        )

    async def _checked_recipe_browser_call(self, name: str, arguments: dict[str, Any]) -> str:
        """Treat Playwright tool errors as failed submission, not page evidence."""
        result = await self.browser.call(name, arguments)
        if result.startswith((
            "ERROR\n", "Playwright MCP error:", "Navigation blocked:",
            "Browser tool is not available", "Call browser_snapshot before",
        )):
            raise RuntimeError(f"Submission recipe {name} failed: {result[:500]}")
        return result

    async def _execute_recipe(self, recipe: PlatformRecipe, *, challenge_id: str, flag: str = "", purpose: str) -> None:
        for step in recipe.steps:
            data = dict(step.data)
            action = step.action
            if action == "navigate":
                url = step.value or data.get("url", "")
                if not url:
                    raise RuntimeError("Recipe navigate step has no URL")
                url = str(url).replace("{challenge_id}", challenge_id)
                await self._checked_recipe_browser_call("browser_navigate", {"url": url})
            elif action == "click":
                target = step.target or data.get("target", "")
                if not target:
                    raise RuntimeError("Recipe click step has no target")
                await self._checked_recipe_browser_call("browser_snapshot", {})
                await self._checked_recipe_browser_call("browser_click", {"target": target})
            elif action == "type":
                target = step.target or data.get("target", "")
                if not target:
                    raise RuntimeError("Recipe type step has no target")
                await self._checked_recipe_browser_call("browser_snapshot", {})
                arguments: dict[str, Any] = {
                    "target": target,
                    "text": flag if step.value == "{flag}" else step.value,
                }
                if data.get("submit") is True:
                    arguments["submit"] = True
                await self._checked_recipe_browser_call("browser_type", arguments)
            elif action == "fill":
                fields = data.get("fields", [])
                if not fields:
                    raise RuntimeError("Recipe fill step has no fields")
                await self._checked_recipe_browser_call("browser_snapshot", {})
                resolved = [
                    {**field, "value": flag if field.get("value") == "{flag}" else field.get("value")}
                    for field in fields
                ]
                await self._checked_recipe_browser_call("browser_fill_form", {"fields": resolved})
            elif action == "wait_for":
                text = step.value or data.get("text", "")
                if not text and not data.get("time"):
                    raise RuntimeError("Recipe wait_for step has no text or time")
                await self._checked_recipe_browser_call("browser_wait_for", {"text": text, "time": data.get("time")})
            elif action == "snapshot":
                await self._checked_recipe_browser_call("browser_snapshot", {})
            elif action == purpose and purpose == "submit":
                continue

    async def call_browser_tool(self, name: str, arguments: dict[str, Any]) -> str:
        async with self._browser_action_lock:
            return await self.browser.call(name, arguments)

    def browser_tool_specs(self) -> list[dict]:
        return self.browser.browser_tool_specs()

    async def browser_status(self) -> dict[str, Any]:
        return self.browser.status()

    async def browser_start(self) -> dict[str, Any]:
        async with self._browser_action_lock:
            await self.browser.start()
            return self.browser.status()

    async def browser_restart(self) -> dict[str, Any]:
        async with self._browser_action_lock:
            await self.browser.restart()
            return self.browser.status()

    async def browser_close(self) -> dict[str, Any]:
        async with self._browser_action_lock:
            await self.browser.close()
            return self.browser.status()

    def submission_recipe_issue(self) -> str | None:
        return submission_recipe_issue(self.recipes.load(self.base_url), self.base_url)

    def save_recipe(self, data: dict[str, Any]) -> Path:
        try:
            recipe = PlatformRecipe.model_validate(data)
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
                for error in exc.errors()
            )
            raise ValueError(
                "Invalid submit recipe fields: " + problems
                + ". Use action='navigate' with value=<challenge URL containing {challenge_id}>, "
                "then action='type' with target=<CSS selector>, value='{flag}', "
                "and data.submit=true when Enter submits."
            ) from exc
        if not recipe.steps:
            raise RuntimeError("Submit recipe must contain browser steps")
        issue = submission_recipe_issue(recipe, self.base_url)
        if issue:
            raise RuntimeError(issue)
        for step in recipe.steps:
            if step.action == "type" and "submit" in step.data and not isinstance(step.data["submit"], bool):
                raise RuntimeError("Recipe type submit option must be a boolean")
            if step.action == "type" and step.data.get("submit") is True and step.value != "{flag}":
                raise RuntimeError("Recipe can only submit after typing the {flag} placeholder")
            if step.action in {"click", "type"} and not (step.target or step.data.get("target")):
                raise RuntimeError(f"Recipe {step.action} step must contain a target")
            if step.action == "navigate" and not (step.value or step.data.get("url")):
                raise RuntimeError("Recipe navigate step must contain a URL")
            if step.action == "fill" and not step.data.get("fields"):
                raise RuntimeError("Recipe fill step must contain fields")
            if re.search(r"(?i)(cookie|password|authorization|bearer|token)", json.dumps(step.model_dump())):
                raise RuntimeError("Recipe contains credential-like data")
        return self.recipes.save(recipe)

    async def close(self) -> None:
        self.state.close_run()
        await self._environments.stop_all()
        await self.browser.close()
