from __future__ import annotations

import asyncio
import shutil
from types import SimpleNamespace

import pytest

from backend.agents.coordinator_core import do_prepare_challenge, do_spawn_swarm
from backend.agents.coordinator_loop import (
    _auto_spawn_one,
    _drain_deferred_auto_spawns,
    _queue_or_spawn_unsolved,
)
from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.platforms.local import LocalPlatformAdapter
from backend.platforms.models import ChallengeBundle, ChallengeState
from backend.platforms.state import ChallengeStateStore
from backend.preparation import ChallengePreparationManager


class FakePreparationPlatform:
    def __init__(self, count: int = 40) -> None:
        self.challenges = {
            f"challenge-{index}": ChallengeBundle(
                native_id=str(index),
                name=f"challenge-{index}",
                state=ChallengeState.WAITING_FOR_DECISION,
            )
            for index in range(count)
        }
        self.active = 0
        self.max_active = 0
        self.prepared: list[str] = []

    async def list_challenges(self):
        return list(self.challenges.values())

    async def prepare_challenge_package(self, name: str):
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.01)
        self.active -= 1
        self.prepared.append(name)
        self.challenges[name] = self.challenges[name].model_copy(
            update={"state": ChallengeState.READY}
        )
        return {"state": "ready", "message": "prepared"}


@pytest.mark.asyncio
async def test_preparation_manager_queues_all_waiting_challenges_with_limit():
    platform = FakePreparationPlatform(40)
    manager = ChallengePreparationManager(platform, concurrency=4, scan_interval=60)
    await manager.start()
    await asyncio.wait_for(manager._queue.join(), timeout=3)

    assert len(platform.prepared) == 40
    assert platform.max_active == 4
    assert len(manager.drain_events()) == 40
    await manager.stop()


@pytest.mark.asyncio
async def test_stop_joins_tasks_parked_in_scan_sleep():
    platform = FakePreparationPlatform(0)
    manager = ChallengePreparationManager(platform, concurrency=2, scan_interval=30)
    await manager.start()
    await asyncio.sleep(0)
    await asyncio.wait_for(manager.stop(), timeout=3)

    assert manager._scanner is None
    assert manager._workers == []


@pytest.mark.asyncio
async def test_preparation_manager_resumes_interrupted_states_only():
    platform = FakePreparationPlatform(0)
    states = [
        ChallengeState.WAITING_FOR_DECISION,
        ChallengeState.PREPARING,
        ChallengeState.WAITING_FOR_PACKAGE,
        ChallengeState.WAITING_FOR_ENVIRONMENT,
        ChallengeState.READY,
        ChallengeState.NEEDS_INPUT,
        ChallengeState.SOLVED,
    ]
    for index, state in enumerate(states):
        platform.challenges[state.value] = ChallengeBundle(
            native_id=str(index),
            name=state.value,
            state=state,
            source_data={"attachments_scanned": state == ChallengeState.READY},
        )
    manager = ChallengePreparationManager(platform, concurrency=2, scan_interval=60)
    await manager.start()
    await asyncio.wait_for(manager._queue.join(), timeout=2)

    assert set(platform.prepared) == {
        "waiting_for_decision",
        "preparing",
        "waiting_for_package",
    }
    await manager.stop()


@pytest.mark.asyncio
async def test_coordinator_queues_browser_challenges_before_spawn():
    class FakePreparation:
        supported = True

        def __init__(self):
            self.queued = []

        async def enqueue(self, name):
            self.queued.append(name)
            return True

    preparation = FakePreparation()
    deps = CoordinatorDeps(
        platform=SimpleNamespace(),
        cost_tracker=CostTracker(),
        settings=SimpleNamespace(),
    )
    poller = SimpleNamespace(
        known_challenges={"remote", "attachment"},
        known_solved=set(),
    )

    await _queue_or_spawn_unsolved(deps, poller, preparation)

    assert preparation.queued == ["attachment", "remote"]
    assert deps.swarms == {}


@pytest.mark.asyncio
async def test_full_capacity_defers_and_later_starts_ready_challenge(monkeypatch):
    gate = asyncio.Event()
    running = asyncio.create_task(gate.wait())
    deps = CoordinatorDeps(
        platform=SimpleNamespace(),
        cost_tracker=CostTracker(),
        settings=SimpleNamespace(),
        max_concurrent_challenges=1,
    )
    deps.swarm_tasks["first"] = running
    spawned = []

    async def fake_spawn(_deps, name):
        spawned.append(name)
        return f"Swarm spawned for {name} with 1 models"

    monkeypatch.setattr("backend.agents.coordinator_core.do_spawn_swarm", fake_spawn)
    assert await _auto_spawn_one(deps, "second") == "At capacity for second"
    assert deps.deferred_auto_spawn == {"second"}
    assert spawned == []

    gate.set()
    await running
    messages = await _drain_deferred_auto_spawns(deps, set())
    assert spawned == ["second"]
    assert messages == ["Swarm spawned for second with 1 models"]
    assert deps.deferred_auto_spawn == set()


@pytest.mark.asyncio
async def test_cancelled_swarm_keeps_capacity_until_task_finishes():
    gate = asyncio.Event()
    running = asyncio.create_task(gate.wait())
    cancelled = asyncio.Event()
    cancelled.set()
    deps = CoordinatorDeps(
        platform=SimpleNamespace(),
        cost_tracker=CostTracker(),
        settings=SimpleNamespace(),
        model_specs=["fake"],
        no_submit=True,
        max_concurrent_challenges=1,
    )
    deps.swarms["first"] = SimpleNamespace(cancel_event=cancelled)
    deps.swarm_tasks["first"] = running
    try:
        message = await do_spawn_swarm(deps, "second")
        assert message.startswith("At capacity")
        assert "first" in deps.swarms
    finally:
        gate.set()
        await running


@pytest.mark.asyncio
async def test_local_coordinator_uses_actual_challenge_directory(tmp_path, monkeypatch):
    root = tmp_path / "challenges"
    actual = root / "original-folder"
    (actual / "distfiles").mkdir(parents=True)
    (actual / "distfiles" / "input.txt").write_text("fixture", encoding="utf-8")
    (actual / "metadata.yml").write_text(
        "name: Display Name\ncategory: misc\ndescription: Local fixture\n", encoding="utf-8"
    )
    settings = Settings(
        _env_file=None,
        platform="local",
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
        knowledge_enabled=False,
    )
    platform = LocalPlatformAdapter(str(root), settings=settings)
    await platform.start()
    deps = CoordinatorDeps(
        platform=platform,
        cost_tracker=CostTracker(),
        settings=settings,
        challenges_root=str(root),
        model_specs=["fake"],
        no_submit=True,
    )

    from backend.agents.swarm import ChallengeSwarm

    async def fake_run(self):
        return None

    monkeypatch.setattr(ChallengeSwarm, "run", fake_run)
    try:
        await do_prepare_challenge(deps, "Display Name")
        assert deps.challenge_dirs["Display Name"] == str(actual)
        deps.challenge_dirs.clear()
        deps.challenge_metas.clear()
        result = await do_spawn_swarm(deps, "Display Name")
        assert result.startswith("Swarm spawned")
        assert deps.challenge_dirs["Display Name"] == str(actual)
        await deps.swarm_tasks["Display Name"]
    finally:
        await platform.close()


def test_state_store_releases_sqlite_file_on_windows(tmp_path):
    root = tmp_path / "disposable-state"
    store = ChallengeStateStore(root / "state.sqlite3")
    store.close_run()
    shutil.rmtree(root)
    assert not root.exists()
