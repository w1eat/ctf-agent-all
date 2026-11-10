from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import pytest
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from backend.agents.claude_coordinator import _build_coordinator_mcp
from backend.agents.claude_solver import ClaudeSolver
from backend.agents.codex_coordinator import CodexCoordinator
from backend.agents.codex_solver import CodexSolver
from backend.agents.coordinator_core import do_claim_solver_request, do_reply_to_solver_request
from backend.agents.coordinator_loop import run_event_loop
from backend.agents.solver import Solver, TracingToolset, _build_toolset
from backend.agents.swarm import ChallengeSwarm
from backend.config import Settings
from backend.coordination import CoordinatorRequestBroker, make_claude_coordination_server
from backend.cost_tracker import CostTracker
from backend.deps import CoordinatorDeps
from backend.output_types import SolverGaveUp
from backend.prompts import ChallengeMeta, build_prompt
from backend.solver_base import CANCELLED, GAVE_UP, TIMED_OUT, SolverResult
from backend.tools.sandbox import check_coordinator_request, request_coordinator


@pytest.mark.asyncio
async def test_concurrent_requests_are_correlated_and_preserve_complete_text():
    broker = CoordinatorRequestBroker()
    first_message = 'first\n中文 "quoted" ' + "x" * 6000
    first = asyncio.create_task(broker.request("same challenge", "model/a", first_message, timeout_seconds=2))
    second = asyncio.create_task(broker.request("other challenge", "model/a", "second", timeout_seconds=2))
    third = asyncio.create_task(broker.request("same challenge", "model/b", "third", timeout_seconds=2))
    await asyncio.sleep(0)
    requests = broker.announcements()
    assert len(requests) == 3
    assert "message" not in requests[0]
    assert all(not request["reminder"] for request in requests)
    assert broker.announcements() == []
    reminders = broker.announcements(reminder_seconds=0)
    assert [item["request_id"] for item in reminders] == [item["request_id"] for item in requests]
    assert all(request["reminder"] for request in reminders)

    a, b, c = requests
    assert broker.reply(a["request_id"], b["challenge_name"], b["model_spec"], "answered", "wrong")["status"] == "identity_mismatch"
    assert broker.reply(a["request_id"], c["challenge_name"], c["model_spec"], "answered", "wrong")["status"] == "identity_mismatch"
    assert not first.done() and not second.done() and not third.done()
    assert broker.reply(a["request_id"], a["challenge_name"], a["model_spec"], "answered", "unclaimed")["status"] == "not_claimed"
    for item in requests:
        claimed = broker.claim(item["request_id"], item["challenge_name"], item["model_spec"])
        assert claimed["status"] == "claimed"
        if item is a:
            assert claimed["message"] == first_message
    assert broker.reply(b["request_id"], b["challenge_name"], b["model_spec"], "blocked", "not available")["status"] == "delivered"
    assert broker.reply(c["request_id"], c["challenge_name"], c["model_spec"], "answered", "third result")["status"] == "delivered"
    response = "完整响应\n" + "y" * 9000
    assert broker.reply(a["request_id"], a["challenge_name"], a["model_spec"], "answered", response)["status"] == "delivered"
    assert broker.reply(a["request_id"], a["challenge_name"], a["model_spec"], "answered", "duplicate")["status"] == "not_pending"
    assert (await first)["response"] == response
    assert (await second)["status"] == "blocked"
    assert (await third)["response"] == "third result"
    assert broker.pending() == []


@pytest.mark.asyncio
async def test_timeout_cancellation_and_shutdown_release_requests():
    broker = CoordinatorRequestBroker()
    timeout = asyncio.create_task(broker.request("a", "m", "inspect", timeout_seconds=0.02))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    assert (await timeout)["status"] == "not_started"
    assert broker.reply(request_id, "a", "m", "answered", "late")["status"] == "not_pending"
    assert broker.claim(request_id, "a", "m")["status"] == "not_pending"
    assert broker.check("a", "m", request_id)["status"] == "not_started"

    stop = asyncio.Event()
    cancelled = asyncio.create_task(broker.request("a", "m", "inspect", timeout_seconds=5, cancel_event=stop))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    stop.set()
    assert broker.reply(request_id, "a", "m", "answered", "too late")["status"] == "not_pending"
    assert (await cancelled)["status"] == "cancelled"

    abandoned = asyncio.create_task(broker.request("a", "m", "inspect", timeout_seconds=5))
    await asyncio.sleep(0)
    abandoned.cancel()
    with pytest.raises(asyncio.CancelledError):
        await abandoned
    assert broker.pending() == []

    waiting = asyncio.create_task(broker.request("a", "m", "inspect", timeout_seconds=5))
    await asyncio.sleep(0)
    broker.close()
    assert (await waiting)["status"] == "unavailable"
    assert (await broker.request("a", "m", "inspect", timeout_seconds=1))["status"] == "unavailable"


@pytest.mark.asyncio
async def test_claimed_request_retains_late_reply_and_deduplicates_pending_work():
    broker = CoordinatorRequestBroker()
    waiting = asyncio.create_task(broker.request("a", "m", "submit report", timeout_seconds=0.02))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    assert broker.claim(request_id, "a", "wrong")["status"] == "identity_mismatch"
    assert broker.claim(request_id, "a", "m")["status"] == "claimed"
    assert broker.claim(request_id, "a", "m")["status"] == "already_claimed"
    assert (await waiting) == {
        "request_id": request_id,
        "status": "in_progress",
        "response": "The coordinator claimed this request but has not replied. Check its status before retrying.",
    }
    assert broker.pending()[0]["status"] == "in_progress"
    duplicate = await broker.request("a", "m", "submit report", timeout_seconds=1)
    assert duplicate["request_id"] == request_id
    assert duplicate["status"] == "in_progress"
    assert len(broker.pending()) == 1

    response = "完整的迟到结果\n" + "x" * 9000
    assert broker.reply(request_id, "a", "m", "answered", response)["status"] == "stored"
    assert broker.check("a", "m", request_id)["response"] == response
    assert broker.check("a", "other", request_id)["status"] == "not_found"
    assert broker.check("other", "m", request_id)["status"] == "not_found"
    assert broker.check("a", "m")[0]["status"] == "answered"
    assert broker.reply(request_id, "a", "m", "answered", "duplicate")["status"] == "not_pending"
    assert broker.pending() == []


@pytest.mark.asyncio
async def test_unknown_outcome_is_retained_until_evidence_resolves_it():
    broker = CoordinatorRequestBroker()
    waiting = asyncio.create_task(broker.request("a", "m", "submit", timeout_seconds=1))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    assert broker.claim(request_id, "a", "m")["status"] == "claimed"
    assert broker.reply(request_id, "a", "m", "unknown", "connection lost after submit")["status"] == "delivered"
    assert (await waiting)["status"] == "unknown"
    assert (await broker.request("a", "m", "submit", timeout_seconds=1))["request_id"] == request_id
    assert broker.reply(request_id, "a", "m", "answered", "platform record confirms success")["status"] == "stored"
    assert broker.check("a", "m", request_id)["response"] == "platform record confirms success"


@pytest.mark.asyncio
async def test_cancelled_wait_and_shutdown_preserve_claimed_request():
    broker = CoordinatorRequestBroker()
    waiting = asyncio.create_task(broker.request("a", "m", "submit", timeout_seconds=10))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    assert broker.claim(request_id, "a", "m")["status"] == "claimed"
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    assert broker.check("a", "m", request_id)["status"] == "in_progress"
    broker.close()
    assert broker.check("a", "m", request_id)["status"] == "unknown"
    assert broker.reply(request_id, "a", "m", "answered", "late result")["status"] == "stored"
    assert broker.check("a", "m", request_id)["response"] == "late result"


@pytest.mark.asyncio
async def test_reply_after_deadline_does_not_hide_wait_timeout():
    broker = CoordinatorRequestBroker()
    waiting = asyncio.create_task(broker.request("a", "m", "inspect", timeout_seconds=10))
    await asyncio.sleep(0)
    request_id = broker.pending()[0]["request_id"]
    assert broker.claim(request_id, "a", "m")["status"] == "claimed"
    broker._requests[request_id].deadline = 0
    assert broker.reply(request_id, "a", "m", "answered", "result")["status"] == "stored"
    assert (await waiting)["status"] == "in_progress"
    assert broker.check("a", "m", request_id)["response"] == "result"


@pytest.mark.asyncio
async def test_solver_backends_share_the_same_request_response(monkeypatch):
    async def request(message):
        return {"request_id": "request-1", "status": "answered", "response": message + "\n结果"}

    api = await request_coordinator(SimpleNamespace(deps=SimpleNamespace(request_coordinator=request)), "input")
    codex = CodexSolver.__new__(CodexSolver)
    codex.request_coordinator = request
    assert await codex._exec_tool("request_coordinator", {"message": "input"}) == api

    captured = {}

    def capture_server(name, *, tools):
        captured.update({tool.name: tool for tool in tools})
        return {"name": name}

    monkeypatch.setattr("claude_agent_sdk.create_sdk_mcp_server", capture_server)
    make_claude_coordination_server(request)
    claude = await captured["request_coordinator"].handler({"message": "input"})
    assert claude["content"][0]["text"] == api
    assert json.loads(api)["response"] == "input\n结果"

    async def check(request_id):
        return {"request_id": request_id, "status": "answered", "response": "late result"}

    api = await check_coordinator_request(SimpleNamespace(deps=SimpleNamespace(check_coordinator_request=check)), "id")
    codex.check_coordinator_request = check
    assert await codex._exec_tool("check_coordinator_request", {"request_id": "id"}) == api
    make_claude_coordination_server(request, check)
    claude = await captured["check_coordinator_request"].handler({"request_id": "id"})
    assert claude["content"][0]["text"] == api


@pytest.mark.asyncio
async def test_coordinator_backends_use_same_reply_protocol(monkeypatch):
    deps = CoordinatorDeps(platform=None, cost_tracker=CostTracker(), settings=SimpleNamespace())
    waiting = asyncio.create_task(deps.coordination.request("challenge", "model", "question", timeout_seconds=2))
    await asyncio.sleep(0)
    pending = deps.coordination.pending()[0]
    args = {key: pending[key] for key in ("request_id", "challenge_name", "model_spec")}
    args.update(status="answered", response="observed\nresult")

    captured = {}

    def capture_server(name, **kwargs):
        captured.update({tool.name: tool for tool in kwargs["tools"]})
        return {"name": name}

    monkeypatch.setattr("backend.agents.claude_coordinator.create_sdk_mcp_server", capture_server)
    _build_coordinator_mcp(deps)
    listed = await captured["list_solver_requests"].handler({})
    assert "message" not in json.loads(listed["content"][0]["text"])[0]
    coordinator = CodexCoordinator.__new__(CodexCoordinator)
    coordinator.deps = deps
    claim = {key: args[key] for key in ("request_id", "challenge_name", "model_spec")}
    claim_result = json.loads(await coordinator._dispatch_tool("claim_solver_request", claim))
    assert claim_result["status"] == "claimed"
    assert claim_result["message"] == "question"
    assert json.loads(await coordinator._dispatch_tool("reply_to_solver_request", args))["status"] == "delivered"
    assert (await waiting)["response"] == "observed\nresult"

    waiting = asyncio.create_task(deps.coordination.request("challenge", "model", "second", timeout_seconds=2))
    await asyncio.sleep(0)
    pending = deps.coordination.pending()[0]
    args = {key: pending[key] for key in ("request_id", "challenge_name", "model_spec")}
    claimed = await captured["claim_solver_request"].handler(args)
    assert json.loads(claimed["content"][0]["text"])["status"] == "claimed"
    args.update(status="blocked", response="missing environment")
    reply = await captured["reply_to_solver_request"].handler(args)
    assert json.loads(reply["content"][0]["text"])["status"] == "delivered"
    assert (await waiting)["status"] == "blocked"


@pytest.mark.asyncio
async def test_claude_solver_exposes_and_allows_coordination_tool(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    options = {}

    class Client:
        def __init__(self, *, options: object):
            self.options = options

        async def __aenter__(self):
            options["value"] = self.options
            return self

        async def __aexit__(self, *_args):
            pass

    class Sandbox:
        container_id = "test-container"

        async def start(self):
            pass

        async def exec(self, *_args, **_kwargs):
            return SimpleNamespace(stdout="x86_64", exit_code=0)

        async def stop(self):
            pass

    async def request(_message):
        return {"status": "answered", "response": "ok"}

    monkeypatch.setattr("backend.agents.claude_solver.ClaudeSDKClient", Client)
    solver = ClaudeSolver(
        "claude-sdk/claude-opus-4-6", str(tmp_path),
        ChallengeMeta(name="demo", connection_info="https://example.test", challenge_mode="remote"),
        None, CostTracker(), SimpleNamespace(), request_coordinator=request,
    )
    solver.sandbox = Sandbox()
    try:
        await solver.start()
        sdk_options = options["value"]
        assert "mcp__coordination__request_coordinator" in sdk_options.allowed_tools
        assert "mcp__coordination__check_coordinator_request" in sdk_options.allowed_tools
        assert "coordination" in sdk_options.mcp_servers
        assert "mcp__coordination__request_coordinator" in sdk_options.system_prompt
        hook = sdk_options.hooks["PreToolUse"][0].hooks[0]
        decision = await hook({"hook_event_name": "PreToolUse", "tool_name": "mcp__coordination__request_coordinator",
                               "tool_input": {"message": "inspect"}}, "call-1", None)
        assert decision == {}
    finally:
        await solver.stop()


@pytest.mark.asyncio
async def test_pydantic_solver_waits_without_another_model_call(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    broker = CoordinatorRequestBroker()
    model_calls = []
    received = []

    def model(messages, _info):
        model_calls.append(1)
        if len(model_calls) == 1:
            return ModelResponse(parts=[ToolCallPart("request_coordinator", {"message": "inspect the page"})])
        returns = [part for message in messages for part in message.parts if isinstance(part, ToolReturnPart)]
        received.append(json.loads(returns[-1].content))
        return ModelResponse(parts=[TextPart('{"findings_summary":"observed"}')])

    solver = Solver(
        "openai/gpt-5.4-mini", str(tmp_path), ChallengeMeta(name="challenge"),
        platform=None, cost_tracker=CostTracker(), sandbox=SimpleNamespace(), owns_sandbox=False,
        settings=SimpleNamespace(solver_attempt_timeout_seconds=5, solver_max_cost_usd=0),
    )

    async def request(message):
        return await broker.request("challenge", "openai/gpt-5.4-mini", message, timeout_seconds=2)

    solver.deps.request_coordinator = request
    wrapped = TracingToolset(
        wrapped=_build_toolset(solver.deps), tracer=solver.tracer, loop_detector=solver.loop_detector,
        step_counter=solver._step_count,
    )
    solver._agent = Agent(FunctionModel(model), deps_type=type(solver.deps),
                          output_type=PromptedOutput(SolverGaveUp), toolsets=[wrapped])
    task = asyncio.create_task(solver.run_until_done_or_gave_up())
    try:
        for _ in range(100):
            if broker.pending():
                break
            await asyncio.sleep(0.01)
        request_data = broker.pending()[0]
        assert len(model_calls) == 1
        assert broker.claim(request_data["request_id"], "challenge", "openai/gpt-5.4-mini")["status"] == "claimed"
        broker.reply(request_data["request_id"], "challenge", "openai/gpt-5.4-mini", "answered", "page result")
        assert (await asyncio.wait_for(task, 2)).status == GAVE_UP
        assert len(model_calls) == 2
        assert received[0]["response"] == "page result"
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await solver.stop()


@pytest.mark.asyncio
async def test_pydantic_solver_can_retrieve_a_late_reply(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    broker = CoordinatorRequestBroker()
    calls = []
    received = []

    def model(messages, _info):
        calls.append(1)
        if len(calls) == 1:
            return ModelResponse(parts=[ToolCallPart("request_coordinator", {"message": "inspect"})])
        returns = [part for message in messages for part in message.parts if isinstance(part, ToolReturnPart)]
        result = json.loads(returns[-1].content)
        if len(calls) == 2:
            assert result["status"] == "in_progress"
            request_id = result["request_id"]
            assert broker.reply(request_id, "challenge", "model/a", "answered", "late page result")["status"] == "stored"
            return ModelResponse(parts=[ToolCallPart("check_coordinator_request", {"request_id": request_id})])
        received.append(result)
        return ModelResponse(parts=[TextPart('{"findings_summary":"observed"}')])

    solver = Solver(
        "openai/gpt-5.4-mini", str(tmp_path), ChallengeMeta(name="challenge"),
        platform=None, cost_tracker=CostTracker(), sandbox=SimpleNamespace(), owns_sandbox=False,
        settings=SimpleNamespace(solver_attempt_timeout_seconds=5, solver_max_cost_usd=0),
    )

    async def request(message):
        return await broker.request("challenge", "model/a", message, timeout_seconds=0.03)

    async def check(request_id):
        return broker.check("challenge", "model/a", request_id)

    solver.deps.request_coordinator = request
    solver.deps.check_coordinator_request = check
    wrapped = TracingToolset(
        wrapped=_build_toolset(solver.deps), tracer=solver.tracer, loop_detector=solver.loop_detector,
        step_counter=solver._step_count,
    )
    solver._agent = Agent(FunctionModel(model), deps_type=type(solver.deps),
                          output_type=PromptedOutput(SolverGaveUp), toolsets=[wrapped])
    task = asyncio.create_task(solver.run_until_done_or_gave_up())
    try:
        for _ in range(100):
            if broker.pending():
                break
            await asyncio.sleep(0.001)
        request_id = broker.pending()[0]["request_id"]
        assert broker.claim(request_id, "challenge", "model/a")["status"] == "claimed"
        assert (await asyncio.wait_for(task, 2)).status == GAVE_UP
        assert received[0]["status"] == "answered"
        assert received[0]["response"] == "late page result"
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await solver.stop()


@pytest.mark.asyncio
async def test_solver_can_find_claimed_request_after_attempt_timeout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    broker = CoordinatorRequestBroker()
    calls = []
    received = []

    def model(messages, _info):
        calls.append(1)
        if len(calls) == 1:
            return ModelResponse(parts=[ToolCallPart("request_coordinator", {"message": "submit"})])
        if len(calls) == 2:
            return ModelResponse(parts=[ToolCallPart("check_coordinator_request", {"request_id": ""})])
        returns = [part for message in messages for part in message.parts if isinstance(part, ToolReturnPart)]
        received.extend(json.loads(returns[-1].content))
        return ModelResponse(parts=[TextPart('{"findings_summary":"observed"}')])

    solver = Solver(
        "openai/gpt-5.4-mini", str(tmp_path), ChallengeMeta(name="challenge"),
        platform=None, cost_tracker=CostTracker(), sandbox=SimpleNamespace(), owns_sandbox=False,
        settings=SimpleNamespace(solver_attempt_timeout_seconds=1, solver_max_cost_usd=0),
    )

    async def request(message):
        return await broker.request("challenge", "model/a", message, timeout_seconds=10)

    async def check(request_id):
        return broker.check("challenge", "model/a", request_id)

    solver.deps.request_coordinator = request
    solver.deps.check_coordinator_request = check
    wrapped = TracingToolset(
        wrapped=_build_toolset(solver.deps), tracer=solver.tracer, loop_detector=solver.loop_detector,
        step_counter=solver._step_count,
    )
    solver._agent = Agent(FunctionModel(model), deps_type=type(solver.deps),
                          output_type=PromptedOutput(SolverGaveUp), toolsets=[wrapped])
    task = asyncio.create_task(solver.run_until_done_or_gave_up())
    try:
        for _ in range(100):
            if broker.pending():
                break
            await asyncio.sleep(0.01)
        request_id = broker.pending()[0]["request_id"]
        assert broker.claim(request_id, "challenge", "model/a")["status"] == "claimed"
        assert (await asyncio.wait_for(task, 2)).status == TIMED_OUT
        assert broker.reply(request_id, "challenge", "model/a", "answered", "late result")["status"] == "stored"
        solver.bump("Check your earlier coordinator requests.")
        assert (await solver.run_until_done_or_gave_up()).status == GAVE_UP
        assert received[0]["request_id"] == request_id
        assert received[0]["status"] == "answered"
        assert broker.check("challenge", "model/a", request_id)["response"] == "late result"
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await solver.stop()


@pytest.mark.asyncio
async def test_coordinator_event_loop_delivers_and_replies_to_request(monkeypatch):
    class Platform:
        browser_submission = False

        async def close(self):
            pass

    class Poller:
        def __init__(self, **_kwargs):
            self.known_challenges = set()
            self.known_solved = set()
            self.events = asyncio.Queue()

        async def start(self):
            pass

        async def stop(self):
            pass

        async def get_event(self, timeout):
            return await asyncio.wait_for(self.events.get(), timeout=timeout)

        def wake(self):
            self.events.put_nowait(None)

        def drain_events(self):
            return []

    monkeypatch.setattr("backend.agents.coordinator_loop.CTFdPoller", Poller)
    platform = Platform()
    tracker = CostTracker()
    deps = CoordinatorDeps(platform=platform, cost_tracker=tracker, settings=SimpleNamespace(), no_submit=True)
    waiting = None
    message = "观察已登录页面\n" + "z" * 5000

    async def turn(text):
        nonlocal waiting
        if text.startswith("CTF is LIVE"):
            waiting = asyncio.create_task(deps.coordination.request("challenge", "model", message, timeout_seconds=2))
            return
        line = next(line for line in text.splitlines() if line.startswith("SOLVER REQUEST: "))
        request = json.loads(line.removeprefix("SOLVER REQUEST: "))
        assert "message" not in request
        claim = json.loads(await do_claim_solver_request(deps, request["request_id"], "challenge", "model"))
        assert claim["message"] == message
        await do_reply_to_solver_request(deps, request["request_id"], "challenge", "model", "answered", "actual page")
        raise asyncio.CancelledError

    await asyncio.wait_for(run_event_loop(deps, platform, tracker, turn), 3)
    assert waiting is not None
    assert (await waiting)["response"] == "actual page"


@pytest.mark.asyncio
async def test_kill_swarm_interrupts_running_solver(tmp_path):
    settings = Settings(_env_file=None, knowledge_enabled=False, knowledge_db_path=str(tmp_path / "knowledge.sqlite3"))
    swarm = ChallengeSwarm(str(tmp_path), ChallengeMeta(name="demo"), None, CostTracker(), settings)
    started = asyncio.Event()

    class SolverStub:
        async def run_until_done_or_gave_up(self):
            started.set()
            await asyncio.Event().wait()
            return SolverResult(None, GAVE_UP, "", 0, 0, "")

    task = asyncio.create_task(swarm._run_attempt(SolverStub()))
    await started.wait()
    swarm.kill()
    assert (await asyncio.wait_for(task, 1)).status == CANCELLED


@pytest.mark.asyncio
async def test_verifier_requests_have_distinct_model_identity(tmp_path, monkeypatch):
    settings = Settings(_env_file=None, knowledge_enabled=False, knowledge_db_path=str(tmp_path / "knowledge.sqlite3"))
    swarm = ChallengeSwarm(str(tmp_path), ChallengeMeta(name="demo"), None, CostTracker(), settings)
    swarm.coordination = CoordinatorRequestBroker()

    class Verifier:
        request_coordinator = None
        check_coordinator_request = None
        role = ""

        async def start(self):
            pass

        def bump(self, _message):
            pass

        async def run_until_done_or_gave_up(self):
            answer = await self.request_coordinator("verify evidence")
            checked = await self.check_coordinator_request(answer["request_id"])
            return SolverResult(None, GAVE_UP, checked["response"], 1, 0, "")

        async def stop(self):
            pass

    monkeypatch.setattr(swarm, "_create_solver", lambda _model: Verifier())
    task = asyncio.create_task(swarm._run_independent_verifier("model/a", "FLAG{candidate}"))
    try:
        for _ in range(100):
            if swarm.coordination.pending():
                break
            await asyncio.sleep(0.01)
        request = swarm.coordination.pending()[0]
        assert request["model_spec"] == "model/a#verifier"
        swarm.coordination.claim(request["request_id"], "demo", "model/a#verifier")
        swarm.coordination.reply(request["request_id"], "demo", "model/a#verifier", "answered", "evidence")
        await asyncio.wait_for(task, 1)
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


def test_interactive_capability_and_other_requests_are_exposed(tmp_path):
    path = tmp_path / "metadata.yml"
    path.write_text("name: chat\nconnection_info: https://example.test\ncapabilities: [browser_chat]\n", encoding="utf-8")
    meta = ChallengeMeta.from_yaml(path)
    prompt = build_prompt(meta, [], has_coordinator=True)
    assert "browser_chat" in meta.capabilities
    assert "FIRST ACTION REQUIRED**: Use `request_coordinator`" in prompt
    assert "attachment" in prompt and "environment" in prompt
    assert "FIRST ACTION REQUIRED**: Use `request_coordinator`" not in build_prompt(meta, [], has_coordinator=False)
