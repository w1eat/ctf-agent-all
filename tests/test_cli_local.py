from __future__ import annotations

from types import SimpleNamespace

import click
import pytest

from backend.cli import _run_single
from backend.platforms.models import EnvironmentInfo


@pytest.mark.asyncio
async def test_single_challenge_starts_compose_before_solver(tmp_path, monkeypatch):
    from backend import sandbox, writeups
    from backend.agents import swarm as swarm_module
    from backend.platforms.environments import LocalEnvironmentManager

    directory = tmp_path / "service"
    directory.mkdir()
    (directory / "metadata.yml").write_text(
        "name: service\nenvironment:\n  source: compose\n  compose_file: compose.yml\n  url: http://localhost:8765/\n",
        encoding="utf-8",
    )
    observed = []

    async def fake_cleanup():
        return None

    async def fake_start(self, name, env):
        observed.append("start")
        return EnvironmentInfo(status="ready", source="compose", url="http://localhost:8765/")

    class FakeSwarm:
        def __init__(self, **kwargs):
            observed.append("solver")
            assert kwargs["meta"].connection_info == "http://localhost:8765/"
            self.candidate_registry = SimpleNamespace(records=[])

        async def run(self):
            return None

    class FakeWriteupManager:
        def __init__(self, *args, **kwargs):
            pass

        async def wait_for_pending(self, **kwargs):
            pass

    monkeypatch.setattr(sandbox, "cleanup_orphan_containers", fake_cleanup)
    monkeypatch.setattr(LocalEnvironmentManager, "start", fake_start)
    monkeypatch.setattr(swarm_module, "ChallengeSwarm", FakeSwarm)
    monkeypatch.setattr(writeups, "WriteupManager", FakeWriteupManager)
    settings = SimpleNamespace(
        challenge_state_db_path=str(tmp_path / "state.sqlite3"),
        solver_mcp_config="",
        writeup_model_spec="",
        writeup_timeout_seconds=0,
        writeup_replay_timeout_seconds=0,
    )
    await _run_single(settings, str(directory), ["codex/example"], True, 1)
    assert observed == ["start", "solver"]


@pytest.mark.asyncio
async def test_single_challenge_rejects_missing_package_before_solver(tmp_path, monkeypatch):
    from backend import sandbox

    directory = tmp_path / "empty"
    directory.mkdir()
    (directory / "metadata.yml").write_text("name: empty\n", encoding="utf-8")

    async def fake_cleanup():
        return None

    monkeypatch.setattr(sandbox, "cleanup_orphan_containers", fake_cleanup)
    settings = SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3"))
    with pytest.raises(click.ClickException, match="not ready"):
        await _run_single(settings, str(directory), ["codex/example"], True, 1)
