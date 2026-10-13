from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from backend.agents.coordinator_loop import _guarded_step, _run_shutdown, run_event_loop
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps


class EmptyPlatform:
    browser_submission = False

    def __init__(self) -> None:
        self.closed = 0

    async def list_challenges(self):
        return []

    async def get_solve_status(self):
        return set()

    async def close(self):
        self.closed += 1


@pytest.mark.asyncio
async def test_startup_failure_closes_gateway_and_platform(monkeypatch):
    gateway_closed = []

    class FailedGateway:
        def __init__(self, config):
            self.config = config

        async def start(self):
            raise RuntimeError("MCP startup failed")

        async def close(self):
            gateway_closed.append(True)

    monkeypatch.setattr("backend.solver_mcp.SolverMcpGateway", FailedGateway)
    platform = EmptyPlatform()
    tracker = CostTracker()
    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=tracker,
        settings=SimpleNamespace(solver_mcp_config="fixture"),
        no_submit=True,
    )

    async def turn(_message):
        raise AssertionError("Coordinator should not start")

    with pytest.raises(RuntimeError, match="MCP startup failed"):
        await run_event_loop(deps, platform, tracker, turn)
    assert platform.closed == 1
    assert gateway_closed == [True]


@pytest.mark.asyncio
async def test_fatal_coordinator_turn_returns_error_and_closes_platform():
    platform = EmptyPlatform()
    tracker = CostTracker()
    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=tracker,
        settings=SimpleNamespace(),
        no_submit=True,
    )

    async def turn(_message):
        raise RuntimeError("coordinator transport lost")

    result = await run_event_loop(deps, platform, tracker, turn)
    assert "coordinator transport lost" in result["error"]
    assert platform.closed == 1


@pytest.mark.asyncio
async def test_failed_initial_platform_scan_does_not_start_empty_run():
    class FailedPlatform(EmptyPlatform):
        async def list_challenges(self):
            raise ConnectionError("platform unavailable")

    platform = FailedPlatform()
    tracker = CostTracker()
    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=tracker,
        settings=SimpleNamespace(),
        no_submit=True,
    )

    async def turn(_message):
        raise AssertionError("Coordinator should not start with an unknown challenge list")

    with pytest.raises(ConnectionError, match="platform unavailable"):
        await run_event_loop(deps, platform, tracker, turn)
    assert platform.closed == 1


async def _cancel_periodically(task: asyncio.Task) -> None:
    """Imitate anyio re-delivering cancellation to the coordinator task."""
    while not task.done():
        await asyncio.sleep(0.005)
        task.cancel()


class PreparingPlatform(EmptyPlatform):
    """An empty platform that still runs the preparation queue."""

    async def prepare_challenge_package(self, name: str):
        return {"state": "ready", "message": "prepared"}


@pytest.mark.asyncio
async def test_shutdown_sequence_completes_while_task_keeps_getting_cancelled():
    ran: list[str] = []

    async def cleanup() -> None:
        await asyncio.sleep(0.02)
        ran.append("preparation.stop")
        await asyncio.sleep(0.02)
        ran.append("platform.close")

    async def main() -> None:
        await _run_shutdown(cleanup())

    supervisor = asyncio.create_task(main())
    canceller = asyncio.create_task(_cancel_periodically(supervisor))
    try:
        await asyncio.wait_for(supervisor, timeout=10)
    finally:
        canceller.cancel()
        await asyncio.gather(canceller, return_exceptions=True)

    assert ran == ["preparation.stop", "platform.close"]


@pytest.mark.asyncio
async def test_guarded_step_keeps_running_after_a_failed_step():
    ran: list[str] = []

    async def boom() -> None:
        raise RuntimeError("preparation.stop failed")

    async def ok() -> None:
        ran.append("platform.close")

    await _guarded_step(None, "preparation.stop", boom())
    await _guarded_step(None, "platform.close", ok())

    assert ran == ["platform.close"]


@pytest.mark.asyncio
async def test_run_event_loop_finishes_cleanup_when_cancelled_repeatedly():
    platform = PreparingPlatform()
    tracker = CostTracker()
    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=tracker,
        settings=SimpleNamespace(),
        no_submit=True,
    )
    canceller: asyncio.Task | None = None

    async def turn(_message):
        nonlocal canceller
        coordinator = asyncio.current_task()
        canceller = asyncio.create_task(_cancel_periodically(coordinator))
        raise asyncio.CancelledError

    runner = asyncio.create_task(run_event_loop(deps, platform, tracker, turn))
    try:
        await asyncio.wait_for(runner, timeout=15)
    finally:
        if canceller is not None:
            canceller.cancel()
            await asyncio.gather(canceller, return_exceptions=True)

    assert platform.closed == 1
