from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.agents import claude_coordinator, codex_coordinator


@pytest.mark.asyncio
async def test_codex_coordinator_start_failure_closes_platform(monkeypatch):
    events = []

    class FakePlatform:
        async def start(self):
            events.append("platform_start")

        async def close(self):
            events.append("platform_close")

    class FakeCoordinator:
        def __init__(self, deps, model):
            pass

        async def start(self):
            events.append("coordinator_start")
            raise RuntimeError("app server unavailable")

        async def stop(self):
            events.append("coordinator_stop")

    tracer = SimpleNamespace(close=lambda: events.append("tracer_close"))
    deps = SimpleNamespace(tracer=tracer)
    monkeypatch.setattr(codex_coordinator, "build_deps", lambda *args: (FakePlatform(), object(), deps))
    monkeypatch.setattr(codex_coordinator, "CodexCoordinator", FakeCoordinator)
    with pytest.raises(RuntimeError, match="app server unavailable"):
        await codex_coordinator.run_codex_coordinator(
            settings=object(), model_specs=["codex/example"]
        )
    assert events == [
        "platform_start", "coordinator_start", "coordinator_stop", "platform_close", "tracer_close"
    ]


@pytest.mark.asyncio
async def test_claude_client_enter_failure_closes_platform(monkeypatch):
    events = []

    class FakePlatform:
        async def start(self):
            events.append("platform_start")

        async def close(self):
            events.append("platform_close")

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            events.append("client_enter")
            raise RuntimeError("SDK unavailable")

        async def __aexit__(self, *args):
            pass

    tracer = SimpleNamespace(close=lambda: events.append("tracer_close"))
    deps = SimpleNamespace(tracer=tracer)
    monkeypatch.setattr(claude_coordinator, "build_deps", lambda *args: (FakePlatform(), object(), deps))
    monkeypatch.setattr(claude_coordinator, "_build_coordinator_mcp", lambda deps: object())
    monkeypatch.setattr(claude_coordinator, "_build_playwright_mcp", lambda deps: None)
    monkeypatch.setattr(claude_coordinator, "ClaudeAgentOptions", lambda **kwargs: object())
    monkeypatch.setattr(claude_coordinator, "ClaudeSDKClient", FakeClient)
    with pytest.raises(RuntimeError, match="SDK unavailable"):
        await claude_coordinator.run_claude_coordinator(
            settings=object(), model_specs=["claude-sdk/example"]
        )
    assert events == ["platform_start", "client_enter", "platform_close", "tracer_close"]
