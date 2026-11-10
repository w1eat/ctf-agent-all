from __future__ import annotations

import asyncio
import sqlite3
from types import SimpleNamespace

import pytest

from backend.agents.claude_coordinator import _build_coordinator_mcp
from backend.agents.codex_coordinator import CodexCoordinator
from backend.agents.coordinator_core import do_spawn_swarm
from backend.agents.coordinator_loop import _catalog_backlog, run_event_loop
from backend.catalog_monitor import CatalogRefreshSchedule
from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.platforms.browser_mcp import BrowserAutoPlatformAdapter
from backend.poller import CTFdPoller, PollEvent
from backend.preparation import ChallengePreparationManager


def make_settings(tmp_path, run_id="catalog-run"):
    return Settings(
        _env_file=None,
        platform_url="https://platform.test",
        browser_profile_dir=str(tmp_path / "profile"),
        browser_download_dir=str(tmp_path / "downloads"),
        platform_recipe_dir=str(tmp_path / "recipes"),
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        challenge_run_id=run_id,
    )


@pytest.mark.asyncio
async def test_catalog_and_sources_survive_resume_without_creating_packages(tmp_path):
    settings = make_settings(tmp_path)
    root = tmp_path / "challenges"
    adapter = BrowserAutoPlatformAdapter(settings, str(root))
    source = {"url": "https://platform.test/round?page=1", "kind": "page", "navigation": "visit all pages"}
    result = adapter.discover_challenges([
        {"native_id": "1", "name": "locked", "locked": True, "category": "web", "points": 100},
        {"native_id": "2", "name": "solved", "solved": True},
    ], sources=[source], scan_complete=True)
    assert result["scan_complete"] is True
    assert adapter.state.list_challenges() == []
    assert not root.exists()

    restored = BrowserAutoPlatformAdapter(settings, str(root))
    restored._restore_state()
    catalog = {item.native_id: item for item in await restored.list_challenges()}
    assert set(catalog) == {"1", "2"}
    assert catalog["1"].source_data["locked"] is True
    assert catalog["1"].points == 100
    assert restored.is_catalog_only("locked")
    assert await restored.get_solve_status() == {"solved"}
    assert restored.catalog_sources()[0]["url"] == source["url"]

    restored.discover_challenges([{"native_id": "1", "name": "locked", "locked": None}])
    assert (await restored.list_challenges())[0].source_data["locked"] is True
    assert len(await restored.list_challenges()) == 2
    restored.discover_challenges([{"native_id": "3", "name": "available", "locked": False}])
    backlog = await _catalog_backlog(restored, await restored.get_solve_status())
    assert [item["name"] for item in backlog] == ["available"]


@pytest.mark.asyncio
async def test_poller_reports_new_and_unlocked_ids_once(tmp_path):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.discover_challenges([
        {"native_id": "1", "name": "A", "locked": True},
        {"native_id": "2", "name": "unknown"},
    ])
    poller = CTFdPoller(adapter)
    await poller._seed()
    adapter.discover_challenges([
        {"native_id": "1", "name": "A", "locked": False},
        {"native_id": "3", "name": "B", "locked": True},
        {"native_id": "4", "name": "C", "locked": False},
    ])
    await poller._poll_once()
    events = {(event.kind, event.challenge_name) for event in poller.drain_events()}
    assert events == {("challenge_unlocked", "A"), ("new_challenge", "B"), ("new_challenge", "C")}

    await poller._poll_once()
    assert poller.drain_events() == []
    adapter.discover_challenges([
        {"native_id": "3", "name": "B", "locked": False},
        {"native_id": "2", "name": "unknown", "locked": False},
    ])
    await poller._poll_once()
    events = {(event.kind, event.challenge_name) for event in poller.drain_events()}
    assert events == {("challenge_unlocked", "B"), ("challenge_available", "unknown")}
    assert {item.name for item in await adapter.list_challenges()} == {"A", "B", "C", "unknown"}


@pytest.mark.asyncio
async def test_registered_locked_challenge_waits_for_unlock(tmp_path):
    settings = make_settings(tmp_path)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    adapter.register_challenge({"native_id": "1", "name": "A", "points": 250,
                                "connection_info": "https://platform.test/A"})
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": True}])
    registered = (await adapter.list_challenges())[0]
    assert registered.source_data["locked"] is True
    assert registered.points == 250
    manager = ChallengePreparationManager(adapter)
    assert not await manager.enqueue("A")
    deps = CoordinatorDeps(platform=adapter, cost_tracker=CostTracker(), settings=settings, no_submit=True)
    assert "locked" in await do_spawn_swarm(deps, "A")

    poller = CTFdPoller(adapter)
    await poller._seed()
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": False}])
    await poller._poll_once()
    assert [(event.kind, event.challenge_name) for event in poller.drain_events()] == [("challenge_unlocked", "A")]
    assert await manager.enqueue("A")
    assert (await adapter.list_challenges())[0].connection_info == "https://platform.test/A"


def test_new_locked_catalog_entry_cannot_be_registered(tmp_path):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": True}])
    with pytest.raises(ValueError, match="locked"):
        adapter.register_challenge({"native_id": "1", "name": "A", "connection_info": "https://platform.test/A"})
    assert adapter.state.list_challenges() == []
    assert not (tmp_path / "challenges").exists()


def test_registration_cannot_conflict_with_discovered_identity(tmp_path):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": False}])
    with pytest.raises(ValueError, match="another challenge ID"):
        adapter.register_challenge({"native_id": "2", "name": "A"})
    with pytest.raises(ValueError, match="another challenge name"):
        adapter.register_challenge({"native_id": "1", "name": "B"})
    assert adapter.state.list_challenges() == []
    assert not (tmp_path / "challenges").exists()


@pytest.mark.asyncio
async def test_catalog_accepts_zero_and_legacy_challenge_ids(tmp_path):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    result = adapter.discover_challenges([
        {"native_id": 0, "name": "zero"},
        {"challenge_id": "other", "name": "legacy"},
        {"native_id": False, "name": "invalid"},
    ])
    assert result["discovered"] == ["zero", "legacy"]
    assert result["errors"][0]["index"] == 2
    assert {item.native_id for item in await adapter.list_challenges()} == {"0", "other"}


@pytest.mark.asyncio
async def test_queued_preparation_rechecks_lock_before_running(tmp_path, monkeypatch):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": False}])
    adapter.register_challenge({"native_id": "1", "name": "A", "connection_info": "https://platform.test/A"})
    calls = []

    async def prepare(name):
        calls.append(name)
        return {"state": "ready"}

    monkeypatch.setattr(adapter, "prepare_challenge_package", prepare)
    manager = ChallengePreparationManager(adapter)
    assert await manager.enqueue("A")
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": True}])
    worker = asyncio.create_task(manager._worker(0))
    try:
        await asyncio.wait_for(manager._queue.join(), 1)
        assert calls == []
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)


def test_sources_are_credential_free_and_can_be_retired(tmp_path):
    settings = make_settings(tmp_path)
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    source = {"url": "https://platform.test/list?page=1", "kind": "api", "navigation": "read the listing"}
    result = adapter.discover_challenges([], sources=[
        source,
        {"url": "https://platform.test/list?access_token=very-secret", "kind": "api"},
        {"url": "https://other.test/list", "kind": "page"},
    ], scan_complete=True)
    assert len(result["source_errors"]) == 2
    assert result["scan_complete"] is False
    assert adapter.catalog_scan_generation == 0
    assert len(adapter.catalog_sources()) == 1
    with sqlite3.connect(settings.challenge_state_db_path) as connection:
        data = " ".join(row[0] for row in connection.execute("SELECT data_json FROM catalog_sources"))
    assert "very-secret" not in data

    adapter.discover_challenges([], sources=[{**source, "active": False}], scan_complete=True)
    assert adapter.catalog_sources() == []
    restored = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    assert restored.catalog_sources() == []
    restored.discover_challenges([], sources=[source], scan_complete=True)
    assert restored.catalog_sources()[0]["url"] == source["url"]


def test_complete_scan_requires_all_sources_and_no_failed_batch(tmp_path):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    first = {"url": "https://platform.test/one", "kind": "page"}
    second = {"url": "https://platform.test/two", "kind": "api"}
    initial = adapter.discover_challenges([], sources=[first, second], scan_complete=True)
    assert initial["scan_complete"] is True
    adapter.begin_catalog_scan()
    partial = adapter.discover_challenges([], sources=[first], scan_complete=True)
    assert partial["scan_complete"] is False
    assert partial["missing_sources"][0]["url"] == second["url"]
    complete = adapter.discover_challenges([], sources=[second], scan_complete=True)
    assert complete["scan_complete"] is True

    adapter.begin_catalog_scan()
    adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": "unknown"}], sources=[first])
    failed = adapter.discover_challenges([], sources=[second], scan_complete=True)
    assert failed["scan_complete"] is False
    assert failed["scan_had_errors"] is True
    adapter.begin_catalog_scan()
    assert adapter.discover_challenges([], sources=[first, second], scan_complete=True)["scan_complete"] is True


@pytest.mark.asyncio
async def test_both_coordinator_backends_forward_catalog_sources(tmp_path, monkeypatch):
    adapter = BrowserAutoPlatformAdapter(make_settings(tmp_path), str(tmp_path / "challenges"))
    deps = CoordinatorDeps(platform=adapter, cost_tracker=CostTracker(), settings=SimpleNamespace())
    tools = {}

    def capture_server(name, **kwargs):
        tools.update({tool.name: tool for tool in kwargs["tools"]})
        return {"name": name}

    monkeypatch.setattr("backend.agents.claude_coordinator.create_sdk_mcp_server", capture_server)
    _build_coordinator_mcp(deps)
    args = {
        "challenges": [{"native_id": "1", "name": "A", "locked": True}],
        "sources": [{"url": "https://platform.test/list", "kind": "page"}],
        "scan_complete": True,
    }
    result = await tools["discover_challenges"].handler(args)
    assert '"scan_complete": true' in result["content"][0]["text"]
    assert adapter.catalog_scan_generation == 1
    assert adapter.catalog_sources()[0]["url"] == "https://platform.test/list"
    coordinator = CodexCoordinator.__new__(CodexCoordinator)
    coordinator.deps = deps
    args["challenges"][0]["locked"] = False
    assert '"scan_complete": true' in await coordinator._dispatch_tool("discover_challenges", args)
    assert adapter.catalog_scan_generation == 2
    assert not adapter.is_challenge_locked("A")


def test_schedule_coalesces_solves_and_retries_with_backoff():
    schedule = CatalogRefreshSchedule(120, 0, debounce_seconds=2, retry_seconds=30)
    schedule.request("solved A", 10)
    schedule.request("solved B", 11)
    assert schedule.wait_seconds(11) == 1
    assert schedule.take_due(11) == []
    assert schedule.take_due(12) == ["solved A", "solved B"]
    schedule.retry(20)
    schedule.request("solved C", 25)
    assert schedule.take_due(27) == ["previous refresh was incomplete", "solved C"]
    schedule.retry(30)
    assert schedule.take_due(89) == []
    assert schedule.take_due(90) == ["previous refresh was incomplete"]
    schedule.succeeded()
    schedule.retry(100)
    assert schedule.take_due(130) == ["previous refresh was incomplete"]
    schedule.request("solved D", 135)
    schedule.retry(135)
    schedule.succeeded(136)
    assert schedule.take_due(200) == []
    assert schedule.take_due(256) == ["periodic refresh"]


@pytest.mark.asyncio
async def test_idle_coordinator_receives_periodic_catalog_refresh(monkeypatch):
    class Platform:
        browser_submission = False
        catalog_scan_generation = 0

        async def close(self):
            pass

        async def list_challenges(self):
            return []

        def discover_challenges(self, *_args, **_kwargs):
            self.catalog_scan_generation += 1

        def catalog_sources(self):
            return [{"url": "https://platform.test/list", "kind": "page"}]

    class Poller:
        def __init__(self, **_kwargs):
            self.known_challenges = set()
            self.known_solved = set()

        async def start(self):
            pass

        async def stop(self):
            pass

        async def get_event(self, timeout):
            await asyncio.sleep(timeout)
            return None

        def drain_events(self):
            return []

        def wake(self):
            pass

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", Poller)
    platform = Platform()
    tracker = CostTracker()
    deps = CoordinatorDeps(platform=platform, cost_tracker=tracker,
                           settings=SimpleNamespace(coordinator_catalog_refresh_interval_seconds=0.02), no_submit=True)
    messages = []

    async def turn(message):
        messages.append(message)
        platform.discover_challenges([], scan_complete=True)
        if "CATALOG REFRESH:" in message:
            raise asyncio.CancelledError

    await asyncio.wait_for(run_event_loop(deps, platform, tracker, turn), 2)
    refresh = next(message for message in messages if "CATALOG REFRESH:" in message)
    assert "periodic refresh" in refresh
    assert "https://platform.test/list" in refresh


@pytest.mark.asyncio
async def test_solve_triggers_refresh_and_incomplete_scan_retries(monkeypatch):
    class Platform:
        browser_submission = False
        catalog_scan_generation = 0

        async def close(self):
            pass

        async def list_challenges(self):
            return []

        def discover_challenges(self, *_args, **_kwargs):
            self.catalog_scan_generation += 1

        def catalog_sources(self):
            return []

    class Poller:
        def __init__(self, **_kwargs):
            self.known_challenges = {"A"}
            self.known_solved = {"A"}
            self.events = [PollEvent("challenge_solved", "A")]

        async def start(self):
            pass

        async def stop(self):
            pass

        async def get_event(self, timeout):
            if self.events:
                return self.events.pop()
            await asyncio.sleep(timeout)
            return None

        def drain_events(self):
            return []

        def wake(self):
            pass

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", Poller)
    monkeypatch.setattr(
        "backend.agents.coordinator_loop.CatalogRefreshSchedule",
        lambda interval, started: CatalogRefreshSchedule(interval, started, debounce_seconds=0.01, retry_seconds=0.02),
    )
    platform = Platform()
    tracker = CostTracker()
    deps = CoordinatorDeps(platform=platform, cost_tracker=tracker,
                           settings=SimpleNamespace(coordinator_catalog_refresh_interval_seconds=0), no_submit=True)
    refreshes = []

    async def turn(message):
        if message.startswith("CTF is LIVE"):
            platform.discover_challenges([], scan_complete=True)
        elif "CATALOG REFRESH:" in message:
            refreshes.append(message)
            if len(refreshes) == 2:
                platform.discover_challenges([], scan_complete=True)
                raise asyncio.CancelledError

    await asyncio.wait_for(run_event_loop(deps, platform, tracker, turn), 2)
    assert "platform confirmed A" in refreshes[0]
    assert "previous refresh was incomplete" in refreshes[1]


@pytest.mark.asyncio
@pytest.mark.parametrize(("event_kind", "retired", "should_restart"), [
    ("challenge_available", False, False),
    ("challenge_available", True, False),
    ("new_challenge", True, False),
    ("challenge_unlocked", False, True),
    ("challenge_unlocked", True, True),
])
async def test_only_real_unlock_retries_a_finished_swarm(monkeypatch, event_kind, retired, should_restart):
    class Platform:
        browser_submission = False

        async def close(self):
            pass

        async def list_challenges(self):
            return []

    class Poller:
        def __init__(self, **_kwargs):
            self.known_challenges = set()
            self.known_solved = set()
            self.events = [PollEvent(event_kind, "A")]

        async def start(self):
            pass

        async def stop(self):
            pass

        async def get_event(self, timeout):
            return self.events.pop() if self.events else None

        def drain_events(self):
            return []

        def wake(self):
            pass

    attempts = []

    async def spawn(_deps, name):
        attempts.append(name)
        return f"Swarm spawned for {name}"

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", Poller)
    monkeypatch.setattr("backend.agents.coordinator_loop._auto_spawn_one", spawn)
    platform = Platform()
    tracker = CostTracker()
    deps = CoordinatorDeps(platform=platform, cost_tracker=tracker, settings=SimpleNamespace(), no_submit=True)
    completed = asyncio.get_running_loop().create_future()
    completed.set_result(None)
    deps.started_challenges.add("A")
    if not retired:
        deps.swarm_tasks["A"] = completed
        deps.swarms["A"] = SimpleNamespace(kill=lambda: None)

    async def turn(message):
        if not message.startswith("CTF is LIVE"):
            raise asyncio.CancelledError

    await asyncio.wait_for(run_event_loop(deps, platform, tracker, turn), 2)
    assert bool(attempts) is should_restart


@pytest.mark.asyncio
async def test_periodic_scan_discovers_unlock_and_queues_both_challenges(tmp_path, monkeypatch):
    settings = make_settings(tmp_path)
    settings.coordinator_catalog_refresh_interval_seconds = 1
    adapter = BrowserAutoPlatformAdapter(settings, str(tmp_path / "challenges"))
    tracker = CostTracker()
    deps = CoordinatorDeps(platform=adapter, cost_tracker=tracker, settings=settings, no_submit=True)
    spawned = []

    async def prepare(name):
        return {"state": "ready", "message": f"{name} ready"}

    async def spawn(_deps, name):
        if name not in spawned:
            spawned.append(name)
        return f"Swarm spawned for {name}"

    async def close():
        pass

    monkeypatch.setattr(adapter, "prepare_challenge_package", prepare)
    monkeypatch.setattr(adapter, "close", close)
    monkeypatch.setattr("backend.agents.coordinator_loop._auto_spawn_one", spawn)
    monkeypatch.setattr(
        "backend.agents.coordinator_loop.CTFdPoller",
        lambda platform, interval_s: CTFdPoller(platform, interval_s=0.01),
    )
    monkeypatch.setattr(
        "backend.agents.coordinator_loop.ChallengePreparationManager",
        lambda platform, concurrency: ChallengePreparationManager(platform, concurrency=concurrency, scan_interval=0.01),
    )
    observed = []
    source = {"url": "https://platform.test/list", "kind": "page"}

    async def turn(message):
        observed.append(message)
        if message.startswith("CTF is LIVE"):
            adapter.discover_challenges([{"native_id": "1", "name": "A", "locked": True}],
                                        sources=[source], scan_complete=True)
        elif "CATALOG REFRESH:" in message:
            adapter.discover_challenges([
                {"native_id": "1", "name": "A", "locked": False},
                {"native_id": "2", "name": "B", "locked": False},
            ], sources=[source], scan_complete=True)
        else:
            for name, native_id in (("A", "1"), ("B", "2")):
                if (f"'{name}' is catalog-only" in message and not adapter.is_challenge_locked(name)
                        and adapter.is_catalog_only(name)):
                    adapter.register_challenge({"native_id": native_id, "name": name,
                                                "connection_info": f"https://platform.test/{name}"})
        if set(spawned) == {"A", "B"}:
            raise asyncio.CancelledError

    await asyncio.wait_for(run_event_loop(deps, adapter, tracker, turn), 4)
    assert set(spawned) == {"A", "B"}
    assert any("UNLOCKED: 'A'" in message for message in observed)
    assert any("DISCOVERED: 'B'" in message for message in observed)
