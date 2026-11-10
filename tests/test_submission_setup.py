from __future__ import annotations

from types import SimpleNamespace

import pytest
from claude_agent_sdk import ResultMessage

from backend.agents.claude_coordinator import _coordinator_result_error
from backend.agents.coordinator_core import do_spawn_swarm
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.submission_setup import (
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
async def test_global_flag_recipe_is_not_required():
    platform = FakePlatform()
    turns = []

    async def turn(message):
        turns.append(message)

    state = deps(platform)
    assert await ensure_submission_setup(state, turn) is None
    assert state.submission_setup_complete
    assert turns == []


@pytest.mark.asyncio
async def test_unknown_challenge_workflow_blocks_automatic_solver(tmp_path):
    platform = FakePlatform()
    platform.challenge_submission_workflow = lambda _: None
    state = deps(platform)
    state.challenge_dirs["demo"] = str(tmp_path)
    state.challenge_metas["demo"] = SimpleNamespace()
    result = await do_spawn_swarm(state, "demo")
    assert result.startswith("Submission workflow unknown")
    assert not state.swarms


@pytest.mark.asyncio
async def test_submit_disabled_skips_gate():
    platform = FakePlatform()
    state = deps(platform, no_submit=True)
    assert submission_setup_issue(state) is None
