from __future__ import annotations

import asyncio
import json
import os
import signal
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from rich.console import Console

from backend.agents import claude_coordinator, codex_coordinator
from backend.agents.coordinator_loop import _cleanup_step
from backend.platforms.browser_mcp import BrowserMCPClient
from backend.tracing import (
    CoordinatorTracer,
    cancellation_origin,
    observe_exit_signals,
    prune_run_logs,
    run_text_log,
)


def _events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_trace_keeps_full_payload_and_correlates_incomplete_calls(tmp_path):
    tracer = CoordinatorTracer("run-one", str(tmp_path), "20260924-180000")
    payload = "x" * 120_000
    tracer.turn_input(payload)
    done = tracer.tool_call("browser_snapshot", {"code": payload}, call_id="done")
    tracer.tool_result("browser_snapshot", payload, call_id=done)
    tracer.tool_call("browser_click", {"target": payload}, call_id="pending")
    tracer.close()

    events = _events(tmp_path / "coordinator-run-one-20260924-180000.jsonl")
    assert [event["seq"] for event in events] == list(range(1, len(events) + 1))
    assert all(event["run_id"] == "run-one" and event["utc"].endswith("+00:00") for event in events)
    assert all(event["turn_id"] for event in events)
    assert any(event.get("result") == payload for event in events)
    assert any(event["type"] == "operation_finished" and event["call_id"] == "done"
               and event["status"] == "completed" for event in events)
    assert any(event["type"] == "operation_incomplete" and event["call_id"] == "pending"
               for event in events)


def test_trace_write_failure_is_visible_but_does_not_raise(tmp_path, capsys):
    tracer = CoordinatorTracer("run", str(tmp_path))
    original = tracer._fh

    class BrokenFile:
        def write(self, _value):
            raise OSError("disk full")

        def flush(self):
            pass

    tracer._fh = BrokenFile()
    tracer.event("test")
    assert "Coordinator trace write failed: disk full" in capsys.readouterr().err
    tracer._fh = original
    tracer.close()


def test_signal_observation_does_not_infer_user_action(monkeypatch):
    handlers = {}
    def original(_number, _frame):
        return None
    monkeypatch.setattr(signal, "getsignal", lambda number: original)
    monkeypatch.setattr(signal, "signal", lambda number, handler: handlers.__setitem__(number, handler))

    with observe_exit_signals():
        assert cancellation_origin() == {"origin": "unknown_external_cancel"}
        handlers[signal.SIGINT](signal.SIGINT, None)
        assert cancellation_origin()["signal"] == "SIGINT"
        assert cancellation_origin()["origin"] == "observed_signal"


@pytest.mark.asyncio
async def test_cleanup_step_records_secondary_cancellation(tmp_path):
    tracer = CoordinatorTracer("run", str(tmp_path))

    async def cancelled():
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        await _cleanup_step(tracer, "preparation.stop", cancelled())
    tracer.close()
    events = _events(Path(tracer.path))
    assert any(e["type"] == "operation_finished" and e["operation"] == "preparation.stop"
               and e["status"] == "cancelled" for e in events)


@pytest.mark.asyncio
async def test_playwright_disconnect_and_reconnect_failure_are_linked(tmp_path, monkeypatch):
    tracer = CoordinatorTracer("run", str(tmp_path))
    client = BrowserMCPClient("https://example.test", str(tmp_path / "profile"),
                              str(tmp_path / "downloads"))
    client.tracer = tracer
    client._tool_specs = {"browser_snapshot": {}}

    class BrokenSession:
        async def call_tool(self, _name, _arguments):
            raise RuntimeError("Connection closed")

    def failing_params():
        raise RuntimeError("different task")

    client._session = BrokenSession()
    monkeypatch.setattr(client, "_server_params", failing_params)
    assert await client.call("browser_snapshot") == "Playwright MCP error: different task"
    await client.close()
    tracer.close()
    events = _events(Path(tracer.path))
    assert any(e["type"] == "mcp_connection_failed" and e["error"] == "Connection closed"
               for e in events)
    failed_call = next(e for e in events if e["type"] == "mcp_connection_failed")
    assert any(e["type"] == "operation_started" and e["operation"] == "playwright.restart"
               and e["parent_call_id"] == failed_call["call_id"] for e in events)
    assert any(e["type"] == "operation_finished" and e["operation"] == "playwright.restart"
               and e["status"] == "error" and e["error"] == "different task" for e in events)
    assert any(e["type"] == "operation_finished" and e["operation"] == "browser_snapshot"
               and e["status"] == "error" for e in events)


def test_text_log_and_retention_keep_latest_run(tmp_path, capsys):
    for stamp in ("20260901-100000", "20260902-100000", "20260903-100000"):
        for prefix, suffix in (("coordinator", "jsonl"), ("run", "log")):
            path = tmp_path / f"{prefix}-run-{stamp}.{suffix}"
            path.write_text("x" * 10, encoding="utf-8")
            os.utime(path, (time.time() - 20 * 86400, time.time() - 20 * 86400))
    with run_text_log("run", "20260904-100000", str(tmp_path)):
        print("terminal output")
        Console().print("rich output")
    assert "terminal output" in (tmp_path / "run-run-20260904-100000.log").read_text(encoding="utf-8")
    assert "rich output" in (tmp_path / "run-run-20260904-100000.log").read_text(encoding="utf-8")
    assert "terminal output" in capsys.readouterr().out
    prune_run_logs(str(tmp_path), keep_run=("run", "20260904-100000"), max_age_days=7,
                   max_bytes=20)
    assert not (tmp_path / "coordinator-run-20260901-100000.jsonl").exists()
    assert (tmp_path / "run-run-20260904-100000.log").exists()


def test_text_log_open_failure_keeps_program_running(tmp_path, capsys):
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("existing file", encoding="utf-8")
    with run_text_log("run", "20260924-180000", str(blocked)):
        print("still running")
    captured = capsys.readouterr()
    assert "Run text log open failed" in captured.err
    assert "still running" in captured.out


def test_retention_size_limit_keeps_newest_run(tmp_path):
    for stamp in ("20260924-100000", "20260924-110000", "20260924-120000"):
        (tmp_path / f"coordinator-run-{stamp}.jsonl").write_text("x" * 20, encoding="utf-8")
    prune_run_logs(str(tmp_path), max_age_days=7, max_bytes=25)
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "coordinator-run-20260924-120000.jsonl"
    ]


@pytest.mark.asyncio
async def test_claude_sdk_turn_records_completion_and_cancellation(tmp_path, monkeypatch):
    tracer = CoordinatorTracer("run", str(tmp_path))
    settings = SimpleNamespace(coordinator_decision_timeout_seconds=0,
                               coordinator_full_access=False)

    class FakeClient:
        cancel = False

        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def query(self, _message):
            pass

        async def receive_response(self):
            if self.cancel:
                raise asyncio.CancelledError()
            yield SimpleNamespace(content="done")

    client = FakeClient()
    platform = SimpleNamespace(start=lambda: asyncio.sleep(0), close=lambda: asyncio.sleep(0))
    deps = SimpleNamespace(tracer=tracer, settings=settings, msg_port=0)
    monkeypatch.setattr(claude_coordinator, "build_deps", lambda *_args: (platform, object(), deps))
    monkeypatch.setattr(claude_coordinator, "_build_coordinator_mcp", lambda _deps: object())
    monkeypatch.setattr(claude_coordinator, "_build_playwright_mcp", lambda _deps: None)
    monkeypatch.setattr(claude_coordinator, "ClaudeAgentOptions", lambda **_kwargs: object())
    monkeypatch.setattr(claude_coordinator, "ClaudeSDKClient", lambda **_kwargs: client)

    async def fake_loop(_deps, _platform, _tracker, turn_fn):
        await turn_fn("normal")
        client.cancel = True
        with pytest.raises(asyncio.CancelledError):
            await turn_fn("cancel")
        return {}

    monkeypatch.setattr(claude_coordinator, "run_event_loop", fake_loop)
    await claude_coordinator.run_claude_coordinator(settings)
    tracer.close()
    turns = [e for e in _events(Path(tracer.path))
             if e["type"] == "operation_finished" and e["operation"] == "claude"]
    assert [e["status"] for e in turns] == ["completed", "cancelled"]


@pytest.mark.asyncio
async def test_codex_turn_records_completion_and_cancellation(tmp_path):
    tracer = CoordinatorTracer("run", str(tmp_path))
    deps = SimpleNamespace(tracer=tracer, settings=SimpleNamespace(
        coordinator_decision_timeout_seconds=0))
    coordinator = codex_coordinator.CodexCoordinator(deps, model="test")
    coordinator._proc = object()
    coordinator._thread_id = "thread"

    async def complete(_method, _params):
        coordinator._turn_done.set()
        return {}

    coordinator._rpc = complete
    await coordinator.turn("normal")

    async def cancel(_method, _params):
        raise asyncio.CancelledError()

    coordinator._rpc = cancel
    with pytest.raises(asyncio.CancelledError):
        await coordinator.turn("cancel")
    tracer.close()
    turns = [e for e in _events(Path(tracer.path))
             if e["type"] == "operation_finished" and e["operation"] == "codex"]
    assert [e["status"] for e in turns] == ["completed", "cancelled"]
