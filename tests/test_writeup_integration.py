from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.agents.coordinator_core import do_confirm_submission, do_spawn_swarm
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.prompts import ChallengeMeta
from backend.solver_base import CANDIDATE_FOUND, FLAG_FOUND, VERIFIED, SolverResult


class RecordingWriteupManager:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple, dict]] = []

    async def record_and_schedule(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return Path(args[0]) / "writeup.md"


def _deps(tmp_path: Path, platform, manager: RecordingWriteupManager) -> CoordinatorDeps:
    meta = ChallengeMeta(name="sample", native_id="sample-id", category="web")
    return CoordinatorDeps(
        platform=platform,
        cost_tracker=CostTracker(),
        settings=SimpleNamespace(
            flag_verification_quorum=2,
            writeup_model_spec="",
        ),
        model_specs=["openai/test-model"],
        challenges_root=str(tmp_path),
        challenge_dirs={"sample": str(tmp_path / "sample")},
        challenge_metas={"sample": meta},
        writeup_manager=manager,
        coordinator_model_spec="claude-sdk/claude-opus-4-6",
    )


@pytest.mark.asyncio
async def test_coordinator_confirmation_creates_writeup_for_exact_flag(tmp_path: Path):
    class Platform:
        async def confirm_submission(self, name, flag, accepted, reason):
            assert (name, flag, accepted) == ("sample", "FLAG{ok}", True)
            return SimpleNamespace(status="correct", display="CORRECT")

    manager = RecordingWriteupManager()
    deps = _deps(tmp_path, Platform(), manager)
    result = await do_confirm_submission(deps, "sample", "FLAG{ok}", True, "accepted")

    assert result == "CORRECT"
    assert deps.results["sample"]["flag"] == "FLAG{ok}"
    assert len(manager.calls) == 1
    args, kwargs = manager.calls[0]
    assert args[2:4] == ("FLAG{ok}", "platform_confirmed")
    assert "model_spec" not in kwargs


@pytest.mark.asyncio
async def test_rejected_coordinator_flag_does_not_create_writeup(tmp_path: Path):
    class Platform:
        async def confirm_submission(self, *_args):
            return SimpleNamespace(status="incorrect", display="INCORRECT")

    manager = RecordingWriteupManager()
    deps = _deps(tmp_path, Platform(), manager)
    await do_confirm_submission(deps, "sample", "FLAG{wrong}", False, "rejected")

    assert manager.calls == []
    assert deps.results == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "verified_by", "expected_source"),
    [
        (VERIFIED, ("solver-a", "solver-b"), "independent_quorum"),
        (CANDIDATE_FOUND, (), "candidate_found"),
        (FLAG_FOUND, (), "candidate_found"),
    ],
)
async def test_swarm_writes_as_soon_as_flag_is_returned(
    tmp_path: Path, monkeypatch, status: str, verified_by: tuple[str, ...], expected_source: str | None
):
    class Platform:
        async def get_challenge_state(self, _name):
            return {"state": "ready"}

        async def get_solve_status(self):
            return set()

    class FakeSwarm:
        def __init__(self, **_kwargs):
            self.confirmed_flag = None

        async def run(self):
            return SolverResult(
                flag="FLAG{ok}",
                status=status,
                findings_summary="test",
                step_count=1,
                cost_usd=0,
                log_path="",
                verified_by=verified_by,
                model_spec="openai/test-model",
            )

    monkeypatch.setattr("backend.agents.swarm.ChallengeSwarm", FakeSwarm)
    manager = RecordingWriteupManager()
    deps = _deps(tmp_path, Platform(), manager)
    await do_spawn_swarm(deps, "sample")
    await asyncio.wait_for(deps.swarm_tasks["sample"], 1)

    if expected_source:
        assert manager.calls[0][0][3] == expected_source
    else:
        assert manager.calls == []


@pytest.mark.asyncio
async def test_swarm_platform_confirmation_writes_writeup(tmp_path: Path, monkeypatch):
    class Platform:
        async def get_challenge_state(self, _name):
            return {"state": "ready"}

        async def get_solve_status(self):
            return {"sample"}

    class FakeSwarm:
        def __init__(self, **_kwargs):
            self.confirmed_flag = "FLAG{ok}"

        async def run(self):
            return SolverResult(
                flag="FLAG{ok}",
                status=FLAG_FOUND,
                findings_summary="platform accepted",
                step_count=1,
                cost_usd=0,
                log_path="",
                model_spec="openai/test-model",
            )

    monkeypatch.setattr("backend.agents.swarm.ChallengeSwarm", FakeSwarm)
    manager = RecordingWriteupManager()
    deps = _deps(tmp_path, Platform(), manager)
    await do_spawn_swarm(deps, "sample")
    await asyncio.wait_for(deps.swarm_tasks["sample"], 1)

    assert manager.calls[0][0][3] == "platform_confirmed"
