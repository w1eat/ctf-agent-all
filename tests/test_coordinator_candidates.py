import asyncio
import json
from types import SimpleNamespace

import pytest

from backend.agents.coordinator_core import (
    do_confirm_submission,
    do_get_solve_status,
    do_spawn_swarm,
    do_submit_flag,
)
from backend.agents.swarm import ChallengeSwarm
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.prompts import ChallengeMeta


def make_deps(tmp_path):
    return CoordinatorDeps(
        platform=SimpleNamespace(browser_submission=False), cost_tracker=CostTracker(),
        settings=SimpleNamespace(), model_specs=["fake/model"],
        challenge_dirs={"demo": str(tmp_path)}, challenge_metas={"demo": ChallengeMeta(name="demo", category="misc")},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["independently verified", "platform confirmed"])
async def test_known_result_does_not_restart_solver(tmp_path, source):
    deps = make_deps(tmp_path)
    deps.results["demo"] = {"flag": "FLAG{known}", "submit": source}
    notice = await do_spawn_swarm(deps, "demo")
    assert "FLAG{known}" in notice
    assert not deps.swarm_tasks
    assert not deps.swarms


@pytest.mark.asyncio
async def test_status_surfaces_verified_results_without_claiming_platform_success(tmp_path):
    deps = make_deps(tmp_path)
    deps.results["demo"] = {"flag": "FLAG{known}", "submit": "independently verified"}

    async def solved():
        return set()

    deps.platform.get_solve_status = solved
    status = json.loads(await do_get_solve_status(deps))
    assert status["solved"] == []
    assert status["results"] == deps.results


@pytest.mark.asyncio
@pytest.mark.parametrize("via_confirmation", [True, False])
async def test_platform_rejection_allows_reanalysis(tmp_path, monkeypatch, via_confirmation):
    deps = make_deps(tmp_path)
    deps.results["demo"] = {"flag": "FLAG{known}", "submit": "independently verified"}

    async def reject(*args):
        return SimpleNamespace(status="incorrect", display="INCORRECT")

    deps.platform.submit_flag = reject
    deps.platform.confirm_submission = reject
    if via_confirmation:
        await do_confirm_submission(deps, "demo", " FLAG{known} ", False, "Platform rejected")
    else:
        await do_submit_flag(deps, "demo", "FLAG{known}")
    assert deps.results["demo"]["submit"] == "platform rejected"

    async def run(self):
        return None

    monkeypatch.setattr(ChallengeSwarm, "__post_init__", lambda self: None)
    monkeypatch.setattr(ChallengeSwarm, "run", run)
    assert (await do_spawn_swarm(deps, "demo")).startswith("Swarm spawned")
    await deps.swarm_tasks["demo"]


@pytest.mark.asyncio
async def test_concurrent_spawn_calls_create_only_one_swarm(tmp_path, monkeypatch):
    deps = make_deps(tmp_path)
    ready = asyncio.Event()
    started = 0

    async def package(name):
        nonlocal started
        started += 1
        if started == 2:
            ready.set()
        await ready.wait()
        return {"state": "ready"}

    async def run(self):
        return None

    deps.platform.get_challenge_state = package
    monkeypatch.setattr(ChallengeSwarm, "__post_init__", lambda self: None)
    monkeypatch.setattr(ChallengeSwarm, "run", run)
    notices = await asyncio.gather(do_spawn_swarm(deps, "demo"), do_spawn_swarm(deps, "demo"))
    assert sum(message.startswith("Swarm spawned") for message in notices) == 1
    assert sum(message.startswith("Swarm still running") for message in notices) == 1
    await deps.swarm_tasks["demo"]
