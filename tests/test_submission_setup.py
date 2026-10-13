from __future__ import annotations

from types import SimpleNamespace

import pytest
from claude_agent_sdk import ResultMessage

from backend.agents.claude_coordinator import _coordinator_result_error
from backend.agents.coordinator_core import do_spawn_swarm
from backend.agents.coordinator_loop import run_event_loop
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.submission_setup import (
    CoordinatorTurnError,
    ensure_submission_setup,
    submission_setup_issue,
)


class FakePlatform:
    browser_submission = True
    base_url = "https://platform.test"

    def __init__(self, issue="No submit recipe is available"):
        self.issue = issue
        self.closed = False

    def submission_recipe_issue(self):
        return self.issue

    async def list_challenges(self):
        return [SimpleNamespace(
            name="demo", native_id="42", challenge_url="https://platform.test/challenges/42",
        )]

    async def close(self):
        self.closed = True


def test_claude_api_error_retains_model_failure_reason():
    result = ResultMessage(
        subtype="error_during_execution", duration_ms=0, duration_api_ms=0,
        is_error=True, num_turns=1, session_id="test", api_error_status=503,
        result="API Error: 503 model_not_found for gpt-6-luna",
    )
    error = _coordinator_result_error(result)
    assert "HTTP 503" in str(error)
    assert "model_not_found" in str(error)


def deps(platform, *, no_submit=False):
    return CoordinatorDeps(
        platform=platform, cost_tracker=CostTracker(),
        settings=SimpleNamespace(solver_mcp_config=""),
        model_specs=["fake/model"], no_submit=no_submit,
    )


@pytest.mark.asyncio
async def test_existing_recipe_does_not_require_coordinator_setup_turn():
    platform = FakePlatform(issue=None)
    turns = []

    async def turn(message):
        turns.append(message)

    assert await ensure_submission_setup(deps(platform), turn) is None
    assert turns == []


@pytest.mark.asyncio
async def test_coordinator_saves_recipe_before_solving():
    platform = FakePlatform()
    turns = []

    async def turn(message):
        turns.append(message)
        assert "{challenge_id}" in message and "{flag}" in message
        assert "Do NOT enter any flag" in message
        assert '"action":"navigate"' in message
        assert '"data":{"submit":true}' in message
        assert "https://platform.test/challenges/42" in message
        platform.issue = None
        # A model can try to spawn in the same turn after saving; code must
        # keep the gate closed until the setup turn itself has completed.
        assert (await do_spawn_swarm(state, "demo")).startswith("Submission setup required")

    state = deps(platform)
    assert await ensure_submission_setup(state, turn) is None
    assert state.submission_setup_complete
    assert len(turns) == 1


@pytest.mark.asyncio
async def test_missing_recipe_fails_closed_before_poller_and_solvers(monkeypatch):
    platform = FakePlatform()
    state = deps(platform)

    def forbidden_poller(*_args, **_kwargs):
        raise AssertionError("poller started before submission setup")

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", forbidden_poller)
    turns = []

    async def turn(message):
        turns.append(message)
        assert "Do NOT spawn swarms" in message
        blocked = await do_spawn_swarm(state, "demo")
        assert blocked.startswith("Submission setup required")

    result = await run_event_loop(state, platform, state.cost_tracker, turn)
    assert len(turns) == 3
    assert "Submission setup failed" in result["error"]
    assert platform.closed
    assert not state.swarms


@pytest.mark.asyncio
async def test_submit_disabled_skips_gate():
    platform = FakePlatform()
    state = deps(platform, no_submit=True)
    assert submission_setup_issue(state) is None


@pytest.mark.asyncio
async def test_missing_recipe_blocks_even_direct_spawn():
    state = deps(FakePlatform())
    assert (await do_spawn_swarm(state, "demo")).startswith("Submission setup required")
    assert not state.swarms


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", [
    "Coordinator model error: HTTP 503: model_not_found",
    "Coordinator turn timed out after 300s",
])
async def test_coordinator_failure_is_reported_without_starting_poller(monkeypatch, reason):
    platform = FakePlatform()
    state = deps(platform)
    turns = []

    def forbidden_poller(*_args, **_kwargs):
        raise AssertionError("poller started after coordinator failure")

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", forbidden_poller)

    async def turn(message):
        turns.append(message)
        raise CoordinatorTurnError(reason)

    result = await run_event_loop(state, platform, state.cost_tracker, turn)
    assert reason in result["error"]
    assert "No submit recipe is available" not in result["error"]
    assert len(turns) == 1
    assert platform.closed
    assert not state.swarms
