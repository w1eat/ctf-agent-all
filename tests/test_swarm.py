from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import MethodType

import pytest

from backend.agents.swarm import ChallengeSwarm
from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.prompts import ChallengeMeta
from backend.solver_base import (
    BLOCKED,
    CANDIDATE_FOUND,
    ERROR,
    FLAG_FOUND,
    GAVE_UP,
    QUOTA_ERROR,
    VERIFIED,
    SolverResult,
)


class FakePlatform:
    browser_submission = False


class FakeSolver:
    def __init__(self, model_spec: str, results: list[SolverResult], delay: float = 0) -> None:
        self.model_spec = model_spec
        self.agent_name = model_spec
        self.sandbox = None
        self.results = list(results)
        self.delay = delay
        self.calls = 0
        self.bumps = 0
        self.stopped = False

    async def start(self) -> None:
        return None

    async def run_until_done_or_gave_up(self) -> SolverResult:
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.results.pop(0) if len(self.results) > 1 else self.results[0]

    def bump(self, insights: str) -> None:
        self.bumps += 1
        self.last_insights = insights

    def detach_sandbox(self):
        sandbox = self.sandbox
        self.sandbox = None
        return sandbox

    async def stop(self) -> None:
        self.stopped = True


def result(status: str, *, flag: str | None = None, steps: int = 1, cost: float = 0.01) -> SolverResult:
    return SolverResult(flag, status, status, steps, cost, "trace.jsonl")


def make_swarm(tmp_path, model_specs: list[str], attempts: int = 3) -> ChallengeSwarm:
    settings = Settings(
        _env_file=None,
        knowledge_enabled=False,
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
        max_attempts_per_challenge=attempts,
    )
    return ChallengeSwarm(
        challenge_dir=str(tmp_path),
        meta=ChallengeMeta(name="demo", category="misc"),
        platform=FakePlatform(),
        cost_tracker=CostTracker(),
        settings=settings,
        model_specs=model_specs,
        no_submit=True,
    )


@pytest.mark.asyncio
async def test_blocked_solver_does_not_cancel_sibling_that_finds_flag(tmp_path, monkeypatch):
    swarm = make_swarm(tmp_path, ["blocked-model", "winning-model"])
    solvers = {
        "blocked-model": FakeSolver("blocked-model", [result(BLOCKED)]),
        "winning-model": FakeSolver(
            "winning-model", [result(FLAG_FOUND, flag="FLAG{ok}")], delay=0.01
        ),
    }
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: solvers[spec])

    final = await swarm.run()

    assert final is not None
    assert final.status == FLAG_FOUND
    assert final.flag == "FLAG{ok}"
    assert solvers["winning-model"].calls == 1


@pytest.mark.asyncio
async def test_solver_stops_at_per_model_attempt_limit(tmp_path, monkeypatch):
    swarm = make_swarm(tmp_path, ["model"], attempts=3)
    solver = FakeSolver("model", [result(GAVE_UP)])
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: solver)

    async def skip_cooldown(awaitable, timeout):
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr("backend.agents.swarm.asyncio.wait_for", skip_cooldown)

    final = await swarm.run()

    assert final is not None
    assert final.status == GAVE_UP
    assert solver.calls == 3
    assert solver.bumps == 2


@pytest.mark.asyncio
async def test_planetary_clues_trigger_auto_retrieval_before_retry(tmp_path, monkeypatch):
    """Sanitized terms from saved Planetary trace; no live challenge is contacted."""
    swarm = make_swarm(tmp_path, ["model"], attempts=2)
    swarm.meta = ChallengeMeta(name="Planetary Probe", category="web")
    fixture = json.loads((Path(__file__).parent / "fixtures" / "planetary-retrieval-clues.json")
                         .read_text(encoding="utf-8"))
    assert fixture["verification_status"] == "unconfirmed"
    clue = "; ".join(fixture["technical_terms"]) + " privilege check"
    first = SolverResult(None, GAVE_UP, clue, 3, 0.01, "saved-trace")
    second = result(GAVE_UP)
    solver = FakeSolver("model", [first, second])

    class FakeTracer:
        def __init__(self):
            self.events = []

        def event(self, name, **fields):
            self.events.append((name, fields))

    class FakeKnowledge:
        initial_context_audit = {}
        external = type("Snapshot", (), {"snapshot_id": "external-v5"})()
        local = type("Snapshot", (), {"snapshot_id": "local-v1"})()

        def __init__(self):
            self.queries = []

        async def search_async(self, query, **kwargs):
            self.queries.append(query)
            return [{"source": "local-curated", "document_id": "local:card",
                     "path": "knowledge/local/postgresql-boolean-injection.md",
                      "verification_status": "pending",
                     "snippet": "Compare repeatable true and false responses."}]

    solver.tracer = FakeTracer()
    knowledge = FakeKnowledge()
    swarm.knowledge_service = knowledge

    async def skip_cooldown(awaitable, timeout):
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr("backend.agents.swarm.asyncio.wait_for", skip_cooldown)
    await swarm._run_solver_loop(solver, "model")
    assert len(knowledge.queries) == 1
    assert "PostgreSQL" in knowledge.queries[0]
    assert "boolean oracle" in knowledge.queries[0]
    assert "local:card" in solver.last_insights
    assert "[local-curated; pending]" in solver.last_insights
    assert len(solver.last_insights) < 1400
    events = [fields for name, fields in solver.tracer.events if name == "knowledge_auto_search"]
    assert events and events[0]["document_ids"] == ["local:card"]
    assert events[0]["external_snapshot"] == "external-v5"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "findings", "steps", "cost", "expected_searches"),
    [
        (GAVE_UP, "", 3, 0.01, 0),
        (GAVE_UP, "PostgreSQL boolean oracle observed", 0, 0.0, 0),
        (ERROR, "Error: PostgreSQL transport unavailable", 3, 0.01, 0),
        (ERROR, "PostgreSQL boolean oracle observed; later command failed", 3, 0.01, 1),
        (GAVE_UP, "COPY ... TO PROGRAM exit status oracle observed", 3, 0.01, 1),
        (GAVE_UP, "COPY FROM/TO PROGRAM exit status oracle observed", 3, 0.01, 1),
        (QUOTA_ERROR, "PostgreSQL boolean oracle observed", 3, 0.01, 0),
    ],
)
async def test_retry_auto_retrieval_requires_substantive_findings(
    tmp_path, monkeypatch, status, findings, steps, cost, expected_searches,
):
    swarm = make_swarm(tmp_path, ["model"], attempts=2)
    first = SolverResult(None, status, findings, steps, cost, "trace.jsonl")
    solver = FakeSolver("model", [first, result(GAVE_UP)])

    class FakeKnowledge:
        external = type("Snapshot", (), {"snapshot_id": "upstream"})()
        local = type("Snapshot", (), {"snapshot_id": "local"})()

        def __init__(self):
            self.queries = []

        async def search_async(self, query, **_kwargs):
            self.queries.append(query)
            return []

    knowledge = FakeKnowledge()
    swarm.knowledge_service = knowledge

    async def skip_cooldown(awaitable, timeout):
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr("backend.agents.swarm.asyncio.wait_for", skip_cooldown)
    await swarm._run_solver_loop(solver, "model")

    assert len(knowledge.queries) == expected_searches
    if status == QUOTA_ERROR or not steps and not cost:
        assert solver.bumps == 0
    else:
        assert solver.bumps == 1


@pytest.mark.asyncio
async def test_zero_work_quota_handoff_does_not_consume_fallback_attempts(tmp_path, monkeypatch):
    original_spec = "claude-sdk/claude-opus-4-6"
    swarm = make_swarm(tmp_path, [original_spec], attempts=3)
    original = FakeSolver(original_spec, [result(QUOTA_ERROR, steps=0, cost=0)])
    fallback = FakeSolver("bedrock/us.anthropic.claude-opus-4-6-v1", [result(GAVE_UP)])
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: original)

    async def skip_cooldown(awaitable, timeout):
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr("backend.agents.swarm.asyncio.wait_for", skip_cooldown)

    def create_fallback(self, model_spec, sandbox=None, owns_sandbox=None):
        assert model_spec == fallback.model_spec
        return fallback

    swarm._create_pydantic_solver = MethodType(create_fallback, swarm)

    final = await swarm.run()

    assert final is not None
    assert original.calls == 1
    assert fallback.calls == 3


@pytest.mark.asyncio
async def test_single_solver_candidate_requires_fresh_verifier(tmp_path, monkeypatch):
    swarm = make_swarm(tmp_path, ["model"], attempts=1)
    proposer = FakeSolver("model", [result(CANDIDATE_FOUND, flag="FLAG{ok}")])
    verifier = FakeSolver("model", [result(CANDIDATE_FOUND, flag="FLAG{ok}")])
    created = iter([proposer, verifier])
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: next(created))

    final = await swarm.run()

    assert final is not None
    assert final.status == VERIFIED
    assert final.flag == "FLAG{ok}"
    assert proposer.calls == 1
    assert verifier.calls == 1


@pytest.mark.asyncio
async def test_submit_configuration_error_does_not_poison_flag_dedup(tmp_path):
    class RecoveringPlatform:
        browser_submission = True

        def __init__(self):
            self.calls = 0

        async def submit_flag(self, _name, _flag):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("No submit recipe is available")
            return type("Submission", (), {"status": "pending", "display": "SUBMISSION_PENDING — inspect page"})()

    swarm = make_swarm(tmp_path, ["model"])
    platform = RecoveringPlatform()
    swarm.platform = platform

    first, confirmed = await swarm.try_submit_flag("FLAG{ok}", "model")
    assert first.startswith("submit_flag error:")
    assert not confirmed
    assert swarm._submitted_flags == set()
    assert swarm._submit_count == {}

    second, confirmed = await swarm.try_submit_flag("FLAG{ok}", "model")
    assert second.startswith("SUBMISSION_PENDING")
    assert not confirmed
    assert platform.calls == 2
    assert swarm._submitted_flags == {"FLAG{ok}"}
    assert swarm._submit_count == {}


@pytest.mark.asyncio
async def test_candidate_writeup_queues_before_independent_verification(tmp_path, monkeypatch):
    swarm = make_swarm(tmp_path, ["model"], attempts=1)
    proposer = FakeSolver("model", [result(CANDIDATE_FOUND, flag="FLAG{ok}")])
    release_verifier = asyncio.Event()
    queued = asyncio.Event()
    calls = []

    class PausedVerifier(FakeSolver):
        async def run_until_done_or_gave_up(self):
            await release_verifier.wait()
            return await super().run_until_done_or_gave_up()

    verifier = PausedVerifier("model", [result(CANDIDATE_FOUND, flag="FLAG{ok}")])
    created = iter([proposer, verifier])
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: next(created))

    class RecordingManager:
        async def record_and_schedule(self, *args, **kwargs):
            calls.append((args, kwargs))
            queued.set()

    swarm.writeup_manager = RecordingManager()
    running = asyncio.create_task(swarm.run())
    await asyncio.wait_for(queued.wait(), 1)
    assert not running.done()
    assert calls[0][0][2:4] == ("FLAG{ok}", "candidate_found")

    release_verifier.set()
    final = await asyncio.wait_for(running, 2)
    assert final is not None and final.status == VERIFIED
