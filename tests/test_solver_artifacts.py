"""Solver output and sandbox artifact handoff tests."""

from __future__ import annotations

import asyncio
import json
import sys
from types import ModuleType, SimpleNamespace

import pytest

from backend.agents.codex_solver import CodexSolver
from backend.agents.coordinator_core import do_spawn_swarm
from backend.agents.solver import Solver
from backend.agents.swarm import ChallengeSwarm
from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.output_types import CandidateFound, FlagFound, SolverGaveUp, solver_output_json_schema
from backend.prompts import ChallengeMeta, build_prompt
from backend.solver_base import ERROR, FLAG_FOUND, GAVE_UP, SolverResult


def test_solver_output_artifact_fields_are_optional() -> None:
    old_output = FlagFound(flag="FLAG{ok}", method="decode")
    assert old_output.solution_steps == []
    assert old_output.exp_paths == []
    assert old_output.exp_run_command == ""

    candidate = CandidateFound(
        flag="FLAG{ok}",
        method="decode",
        solution_steps=["运行脚本"],
        exp_paths=["/challenge/workspace/solve.py"],
        exp_run_command="python3 /challenge/workspace/solve.py",
    )
    assert candidate.solution_steps == ["运行脚本"]
    schema = solver_output_json_schema()
    assert all("exp_paths" in option["properties"] for option in schema["oneOf"][:2])


def test_gave_up_output_is_supported_by_all_provider_schemas() -> None:
    output = SolverGaveUp(findings_summary="PostgreSQL boolean oracle observed")
    assert output.type == "gave_up"
    schema = solver_output_json_schema()
    assert any(option["properties"].get("type") == {"const": "gave_up"}
               and "findings_summary" in option["required"] for option in schema["oneOf"])
    assert "`gave_up`" in build_prompt(ChallengeMeta(name="demo", category="web"), [])


def test_old_solver_result_constructor_keeps_position_fields() -> None:
    result = SolverResult("FLAG{ok}", FLAG_FOUND, "method", 3, 0.1, "trace.jsonl")
    assert result.flag == "FLAG{ok}"
    assert result.exp_paths == ()
    assert result.saved_exp_paths == ()
    assert result.model_spec == ""


def test_platform_confirmation_keeps_exact_flag_and_discards_stale_artifacts() -> None:
    solver = Solver.__new__(Solver)
    solver.deps = SimpleNamespace(confirmed_flag="FLAG{accepted}")
    solver._flag = "FLAG{different}"
    solver._confirmed = False
    solver._findings = "candidate"
    solver._evidence = ("wrong flag evidence",)
    solver._solution_steps = ("错误步骤",)
    solver._exp_paths = ("/challenge/workspace/wrong.py",)
    solver._exp_run_command = "python3 wrong.py"
    solver._step_count = [2]
    solver.model_spec = "azure/example"
    solver.settings = SimpleNamespace(challenge_run_id="test-run")
    solver.agent_name = "test"
    solver.role = "primary_analysis"
    solver.cost_tracker = SimpleNamespace(by_agent={})
    events = []
    solver.tracer = SimpleNamespace(path="trace.jsonl", event=lambda *args, **kwargs: events.append((args, kwargs)))

    result = solver._result(ERROR)

    assert result.status == FLAG_FOUND
    assert result.flag == "FLAG{accepted}"
    assert result.evidence == ()
    assert result.exp_paths == ()
    assert result.solution_steps == ()
    assert result.model_spec == "azure/example"
    assert events[-1][1]["run_id"] == "test-run"


@pytest.mark.asyncio
async def test_swarm_captures_registered_exp_before_solver_stop(tmp_path, monkeypatch) -> None:
    settings = Settings(
        _env_file=None,
        knowledge_enabled=False,
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
    )
    swarm = ChallengeSwarm(
        challenge_dir=str(tmp_path),
        meta=ChallengeMeta(name="demo", category="misc"),
        platform=SimpleNamespace(browser_submission=False),
        cost_tracker=CostTracker(),
        settings=settings,
        model_specs=["fake/model"],
        no_submit=True,
    )

    class FakeSolver:
        model_spec = "fake/model"
        agent_name = "fake/model"
        role = "primary_analysis"
        sandbox = SimpleNamespace(workspace_dir=str(tmp_path / "workspace"))
        stopped = False

        async def start(self) -> None:
            pass

        async def run_until_done_or_gave_up(self) -> SolverResult:
            return SolverResult(
                "FLAG{ok}", FLAG_FOUND, "decode", 1, 0.01, "trace.jsonl",
                exp_paths=("/challenge/workspace/solve.py",),
                model_spec=self.model_spec,
            )

        async def stop(self) -> None:
            self.stopped = True

    solver = FakeSolver()
    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: solver)

    writeups = ModuleType("backend.writeups")
    calls: list[tuple] = []

    def capture(challenge_dir, sandbox, exp_paths, flag, model_spec):
        assert not solver.stopped
        calls.append((challenge_dir, sandbox, exp_paths, flag, model_spec))
        return ("exp/solve.py",)

    writeups.capture_exp_files = capture
    monkeypatch.setitem(sys.modules, "backend.writeups", writeups)

    result = await swarm.run()

    assert result is not None
    assert result.status == FLAG_FOUND
    assert result.saved_exp_paths == ("exp/solve.py",)
    assert solver.stopped
    assert calls == [
        (str(tmp_path), solver.sandbox, ("/challenge/workspace/solve.py",), "FLAG{ok}", "fake/model")
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("confirmed_flag", "expected_flag", "expected_source"),
    [
        ("FLAG{accepted}", "FLAG{accepted}", "platform confirmed"),
        (None, "FLAG{stale}", "candidate (unverified)"),
    ],
)
async def test_solved_name_alone_never_confirms_stale_solver_flag(
    tmp_path, monkeypatch, confirmed_flag, expected_flag, expected_source
):
    class Platform:
        browser_submission = False

        async def get_challenge_state(self, name):
            return {"state": "ready"}

        async def get_solve_status(self):
            return {"demo"}

        def get_confirmed_flag(self, name):
            return confirmed_flag

    settings = Settings(
        _env_file=None,
        knowledge_enabled=False,
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
    )
    meta = ChallengeMeta(name="demo", category="misc")
    deps = CoordinatorDeps(
        platform=Platform(),
        cost_tracker=CostTracker(),
        settings=settings,
        model_specs=["fake/model"],
        no_submit=False,
        challenge_dirs={"demo": str(tmp_path)},
        challenge_metas={"demo": meta},
    )

    async def fake_run(self):
        return SolverResult("FLAG{stale}", FLAG_FOUND, "guess", 1, 0.01, "trace.jsonl")

    monkeypatch.setattr(ChallengeSwarm, "run", fake_run)
    assert (await do_spawn_swarm(deps, "demo")).startswith("Swarm spawned")
    await deps.swarm_tasks["demo"]
    assert deps.results["demo"] == {"flag": expected_flag, "submit": expected_source}


@pytest.mark.asyncio
async def test_already_confirmed_flag_only_accepts_exact_same_value(tmp_path) -> None:
    settings = Settings(
        _env_file=None,
        knowledge_enabled=False,
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
    )
    swarm = ChallengeSwarm(
        challenge_dir=str(tmp_path),
        meta=ChallengeMeta(name="demo", category="misc"),
        platform=SimpleNamespace(browser_submission=False),
        cost_tracker=CostTracker(),
        settings=settings,
        model_specs=[],
    )
    swarm.confirmed_flag = "FLAG{accepted}"

    _, wrong_confirmed = await swarm.try_submit_flag("FLAG{different}", "fake/model")
    _, same_confirmed = await swarm.try_submit_flag(" FLAG{accepted} ", "fake/model")

    assert wrong_confirmed is False
    assert same_confirmed is True
    assert swarm.confirmed_flag == "FLAG{accepted}"


@pytest.mark.asyncio
async def test_codex_structured_output_cannot_replace_platform_confirmed_flag() -> None:
    solver = CodexSolver.__new__(CodexSolver)
    solver._proc = object()
    solver._thread_id = "thread"
    solver._turn_done = asyncio.Event()
    solver._structured_output = None
    solver._turn_error = None
    solver._confirmed = True
    solver._flag = "FLAG{accepted}"
    solver._findings = ""
    solver._evidence = ()
    solver._solution_steps = ()
    solver._exp_paths = ()
    solver._exp_run_command = ""
    solver._step_count = 0
    solver._cost_usd = 0.0
    solver._bump_insights = None
    solver.role = "primary_analysis"
    solver.model_spec = "codex/example"
    solver.settings = SimpleNamespace(solver_attempt_timeout_seconds=0)
    solver.tracer = SimpleNamespace(path="trace.jsonl", event=lambda *args, **kwargs: None)

    async def rpc(method, params):
        assert method == "turn/start"
        solver._structured_output = {
            "type": "flag_found",
            "flag": "FLAG{different}",
            "method": "wrong",
            "exp_paths": ["/challenge/workspace/wrong.py"],
        }
        solver._turn_done.set()

    solver._rpc = rpc
    result = await solver.run_until_done_or_gave_up()

    assert result.status == FLAG_FOUND
    assert result.flag == "FLAG{accepted}"
    assert result.exp_paths == ()


@pytest.mark.asyncio
async def test_pydantic_gave_up_preserves_findings_for_retry() -> None:
    solver = Solver.__new__(Solver)
    findings = "PostgreSQL boolean oracle observed; role privilege remains unverified"

    async def run(*_args, **_kwargs):
        return SimpleNamespace(
            output=SolverGaveUp(findings_summary=findings),
            usage=SimpleNamespace(input_tokens=1, output_tokens=1, cache_read_tokens=0),
            all_messages=lambda: [], new_messages=lambda: [],
        )

    solver._agent = SimpleNamespace(run=run)
    solver.knowledge_query_budget = None
    solver.settings = SimpleNamespace(solver_attempt_timeout_seconds=0)
    solver.deps = SimpleNamespace(confirmed_flag=None)
    solver.cost_tracker = SimpleNamespace(record=lambda *_args, **_kwargs: None, by_agent={})
    solver.tracer = SimpleNamespace(path="trace.jsonl", usage=lambda *_args: None,
                                    event=lambda *_args, **_kwargs: None)
    solver.agent_name = "test"
    solver.model_id = "example"
    solver.model_spec = "azure/example"
    solver.role = "primary_analysis"
    solver._messages = []
    solver._step_count = [2]
    solver._attempt_start_step = [0]
    solver._flag = "FLAG{stale}"
    solver._confirmed = False
    solver._findings = ""
    solver._evidence = ("stale candidate",)
    solver._solution_steps = ("stale step",)
    solver._exp_paths = ("/challenge/workspace/stale.py",)
    solver._exp_run_command = "python3 stale.py"

    result = await solver.run_until_done_or_gave_up()

    assert result.status == GAVE_UP
    assert result.findings_summary == findings
    assert result.flag is None
    assert result.evidence == ()
    assert result.exp_paths == ()


@pytest.mark.asyncio
async def test_claude_gave_up_preserves_findings_for_retry(monkeypatch) -> None:
    from backend.agents.claude_solver import ClaudeSolver

    findings = "PostgreSQL boolean oracle observed; role privilege remains unverified"

    class FakeResultMessage:
        session_id = "session"
        total_cost_usd = 0.01
        usage = {}
        structured_output = {"type": "gave_up", "findings_summary": findings}

    class FakeClient:
        async def query(self, _prompt):
            pass

        async def receive_response(self):
            solver._step_count += 1
            yield FakeResultMessage()

    monkeypatch.setattr("backend.agents.claude_solver.ResultMessage", FakeResultMessage)
    solver = ClaudeSolver.__new__(ClaudeSolver)
    solver._client = FakeClient()
    solver.knowledge_query_budget = None
    solver.settings = SimpleNamespace(solver_attempt_timeout_seconds=0)
    solver.cancel_event = asyncio.Event()
    solver._session_id = None
    solver._bump_insights = None
    solver._step_count = 2
    solver._cost_usd = 0.0
    solver._flag = "FLAG{stale}"
    solver._confirmed = False
    solver._findings = ""
    solver._evidence = ("stale candidate",)
    solver._solution_steps = ("stale step",)
    solver._exp_paths = ("/challenge/workspace/stale.py",)
    solver._exp_run_command = "python3 stale.py"
    solver.cost_tracker = SimpleNamespace(record_tokens=lambda *_args, **_kwargs: None)
    solver.tracer = SimpleNamespace(path="trace.jsonl", event=lambda *_args, **_kwargs: None)
    solver.agent_name = "test"
    solver.model_id = "example"
    solver.role = "primary_analysis"
    solver.model_spec = "claude-sdk/example"

    result = await solver.run_until_done_or_gave_up()

    assert result.status == GAVE_UP
    assert result.findings_summary == findings
    assert result.flag is None
    assert result.evidence == ()
    assert result.exp_paths == ()

    FakeResultMessage.structured_output = None
    next_result = await solver.run_until_done_or_gave_up()
    assert next_result.status == GAVE_UP
    assert next_result.findings_summary == ""


@pytest.mark.asyncio
async def test_codex_gave_up_preserves_findings_for_retry() -> None:
    findings = "PostgreSQL boolean oracle observed; role privilege remains unverified"
    solver = CodexSolver.__new__(CodexSolver)
    solver._proc = object()
    solver._thread_id = "thread"
    solver._turn_done = asyncio.Event()
    solver._structured_output = None
    solver._turn_error = None
    solver._confirmed = False
    solver._flag = "FLAG{stale}"
    solver._findings = ""
    solver._evidence = ("stale candidate",)
    solver._solution_steps = ("stale step",)
    solver._exp_paths = ("/challenge/workspace/stale.py",)
    solver._exp_run_command = "python3 stale.py"
    solver._step_count = 2
    solver._cost_usd = 0.0
    solver._bump_insights = None
    solver.role = "primary_analysis"
    solver.model_spec = "codex/example"
    solver.settings = SimpleNamespace(solver_attempt_timeout_seconds=0)
    solver.tracer = SimpleNamespace(path="trace.jsonl", event=lambda *_args, **_kwargs: None)

    async def rpc(_method, _params):
        solver._structured_output = {"type": "gave_up", "findings_summary": findings}
        solver._turn_done.set()

    solver._rpc = rpc
    result = await solver.run_until_done_or_gave_up()

    assert result.status == GAVE_UP
    assert result.findings_summary == findings
    assert result.flag is None
    assert result.evidence == ()
    assert result.exp_paths == ()

    async def rpc_without_output(_method, _params):
        solver._turn_done.set()

    solver._rpc = rpc_without_output
    next_result = await solver.run_until_done_or_gave_up()
    assert next_result.status == GAVE_UP
    assert next_result.findings_summary == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("has_analysis", [False, True])
async def test_claude_failure_preserves_only_current_attempt_analysis(monkeypatch, has_analysis) -> None:
    from backend.agents.claude_solver import ClaudeSolver

    class FakeTextBlock:
        def __init__(self, text):
            self.text = text

    class FakeAssistantMessage:
        def __init__(self, text):
            self.content = [FakeTextBlock(text)]

    class FakeClient:
        async def query(self, _prompt):
            pass

        async def receive_response(self):
            if has_analysis:
                yield FakeAssistantMessage("PostgreSQL boolean oracle observed")
            raise RuntimeError("transport disconnected")

    monkeypatch.setattr("backend.agents.claude_solver.AssistantMessage", FakeAssistantMessage)
    monkeypatch.setattr("backend.agents.claude_solver.TextBlock", FakeTextBlock)
    solver = ClaudeSolver.__new__(ClaudeSolver)
    solver._client = FakeClient()
    solver.knowledge_query_budget = None
    solver.settings = SimpleNamespace(solver_attempt_timeout_seconds=0)
    solver.cancel_event = asyncio.Event()
    solver._session_id = None
    solver._bump_insights = None
    solver._step_count = 1
    solver._cost_usd = 0.0
    solver._flag = None
    solver._confirmed = False
    solver._findings = "stale previous attempt"
    solver._evidence = ()
    solver._solution_steps = ()
    solver._exp_paths = ()
    solver._exp_run_command = ""
    solver.tracer = SimpleNamespace(path="trace.jsonl", event=lambda *_args, **_kwargs: None)
    solver.agent_name = "test"
    solver.role = "primary_analysis"
    solver.model_spec = "claude-sdk/example"

    result = await solver.run_until_done_or_gave_up()

    assert result.status == ERROR
    if has_analysis:
        assert result.findings_summary == "PostgreSQL boolean oracle observed | Solver error"
    else:
        assert result.findings_summary == "Error: transport disconnected"


@pytest.mark.asyncio
@pytest.mark.parametrize("has_analysis", [False, True])
async def test_codex_failed_turn_preserves_only_current_attempt_analysis(has_analysis) -> None:
    solver = CodexSolver.__new__(CodexSolver)
    messages = []
    if has_analysis:
        messages.append({"method": "item/completed", "params": {"item": {
            "type": "agentMessage", "phase": "commentary",
            "text": "PostgreSQL boolean oracle observed",
        }}})
    messages.append({"method": "turn/completed", "params": {"turn": {
        "status": "failed", "error": {"message": "transport disconnected"},
    }}})
    lines = iter([*(json.dumps(message).encode() + b"\n" for message in messages), b""])

    async def readline():
        return next(lines)

    solver._proc = SimpleNamespace(stdout=SimpleNamespace(readline=readline))
    solver._turn_done = asyncio.Event()
    solver._turn_error = None
    solver._structured_output = None
    solver._pending_responses = {}
    solver._step_count = 1
    solver._findings = ""
    solver.agent_name = "test"
    solver.tracer = SimpleNamespace(event=lambda *_args, **_kwargs: None)

    await solver._read_loop()

    assert solver._turn_error.startswith("transport disconnected")
    if has_analysis:
        assert solver._findings == "PostgreSQL boolean oracle observed | Turn failed"
    else:
        assert solver._findings.startswith("Turn failed:")


@pytest.mark.asyncio
async def test_verifier_error_with_stale_flag_does_not_confirm_candidate(tmp_path, monkeypatch) -> None:
    settings = Settings(
        _env_file=None,
        knowledge_enabled=False,
        knowledge_db_path=str(tmp_path / "knowledge.sqlite3"),
    )
    swarm = ChallengeSwarm(
        challenge_dir=str(tmp_path),
        meta=ChallengeMeta(name="demo", category="misc"),
        platform=SimpleNamespace(browser_submission=False),
        cost_tracker=CostTracker(),
        settings=settings,
        model_specs=["fake/model"],
    )
    swarm.candidate_registry.propose("FLAG{candidate}", "fake/model")
    swarm.candidate_registry.verify("FLAG{candidate}", "fake/model", accepted=True)

    class FailedVerifier:
        role = ""

        async def start(self) -> None:
            pass

        def bump(self, insights: str) -> None:
            pass

        async def run_until_done_or_gave_up(self) -> SolverResult:
            return SolverResult("FLAG{candidate}", ERROR, "turn failed", 0, 0, "trace.jsonl")

        async def stop(self) -> None:
            pass

    monkeypatch.setattr(ChallengeSwarm, "_create_solver", lambda self, spec: FailedVerifier())

    await swarm._run_independent_verifier("fake/model", "FLAG{candidate}")

    assert swarm.candidate_registry.verified("FLAG{candidate}") is None
