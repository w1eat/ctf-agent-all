import asyncio
import json
from types import SimpleNamespace

import pytest
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai.usage import RequestUsage

from backend.agents.solver import Solver, TracingToolset
from backend.cost_tracker import CostTracker
from backend.output_types import SolverGaveUp
from backend.prompts import ChallengeMeta
from backend.solver_base import BUDGET_EXHAUSTED, CANCELLED, ERROR, GAVE_UP, TIMED_OUT


def make_solver(tmp_path, monkeypatch, respond, *, work=None, timeout=0, budget=0, max_steps=0):
    monkeypatch.chdir(tmp_path)
    solver = Solver(
        "openai/gpt-5.4-mini", str(tmp_path), ChallengeMeta(name="accounting"),
        platform=None, cost_tracker=CostTracker(), sandbox=SimpleNamespace(), owns_sandbox=False,
        settings=SimpleNamespace(solver_attempt_timeout_seconds=timeout, solver_max_cost_usd=budget),
    )
    toolsets = []
    if work:
        toolsets.append(TracingToolset(
            wrapped=FunctionToolset(tools=[work]), tracer=solver.tracer, loop_detector=solver.loop_detector,
            step_counter=solver._step_count, max_steps=max_steps, attempt_start=solver._attempt_start_step,
        ))
    solver._agent = Agent(FunctionModel(respond), output_type=PromptedOutput(SolverGaveUp),
                          toolsets=toolsets, retries={"output": 1})
    return solver


@pytest.mark.asyncio
async def test_invalid_output_keeps_paid_responses_and_reuses_failed_history(tmp_path, monkeypatch):
    def respond(messages, info):
        return ModelResponse(parts=[TextPart("{}")], usage=RequestUsage(input_tokens=100, output_tokens=20))

    solver = make_solver(tmp_path, monkeypatch, respond)
    try:
        failed = await solver.run_until_done_or_gave_up()
        assert failed.status == ERROR
        assert failed.cost_usd > 0
        agent_usage = solver.cost_tracker.by_agent[solver.agent_name]
        assert agent_usage.usage.input_tokens == 200
        assert agent_usage.usage.output_tokens == 40
        assert sum(isinstance(m, ModelResponse) for m in solver._messages) == 2
        seen = []

        def recover(messages, info):
            seen.extend(messages)
            return ModelResponse(parts=[TextPart('{"findings_summary":"Recovered"}')],
                                 usage=RequestUsage(input_tokens=100, output_tokens=20))

        solver.bump("Keep the analysis from the previous attempt")
        solver._agent = Agent(FunctionModel(recover), output_type=PromptedOutput(SolverGaveUp))
        result = await solver.run_until_done_or_gave_up()
        assert result.status == GAVE_UP
        assert sum(isinstance(m, ModelResponse) for m in seen) == 2
        assert agent_usage.usage.input_tokens == 300
        assert agent_usage.usage.output_tokens == 60
    finally:
        await solver.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(("mode", "expected"), [
    ("tool_error", ERROR), ("transport_error", ERROR),
    ("timeout", TIMED_OUT), ("cancel", CANCELLED), ("tool_budget", BUDGET_EXHAUSTED),
])
async def test_interrupted_attempts_keep_usage_and_messages(tmp_path, monkeypatch, mode, expected):
    calls = 0
    started = asyncio.Event()

    async def work() -> str:
        started.set()
        if mode in {"cancel", "timeout"}:
            await asyncio.Event().wait()
        if mode == "tool_error":
            raise RuntimeError("tool failed")
        return "work done"

    def respond(messages, info):
        nonlocal calls
        calls += 1
        if mode == "transport_error" and calls > 1:
            raise RuntimeError("transport failed")
        return ModelResponse(parts=[ToolCallPart("work", {}, tool_call_id=f"call-{calls}")],
                             usage=RequestUsage(input_tokens=100, output_tokens=20))

    solver = make_solver(tmp_path, monkeypatch, respond, work=work,
                         timeout=1 if mode == "timeout" else 0, max_steps=1 if mode == "tool_budget" else 0)
    try:
        task = asyncio.create_task(solver.run_until_done_or_gave_up())
        if mode == "cancel":
            await asyncio.wait_for(started.wait(), timeout=5)
            task.cancel()
        result = await asyncio.wait_for(task, timeout=5)
        assert result.status == expected
        usage = solver.cost_tracker.by_agent[solver.agent_name].usage
        responses = 2 if mode == "tool_budget" else 1
        assert usage.input_tokens == responses * 100
        assert usage.output_tokens == responses * 20
        assert result.cost_usd > 0
        assert sum(isinstance(m, ModelResponse) for m in solver._messages) == responses
    finally:
        await solver.stop()


@pytest.mark.asyncio
async def test_cost_budget_stops_before_the_next_paid_request(tmp_path, monkeypatch):
    calls = 0

    async def work() -> str:
        return "continue"

    def respond(messages, info):
        nonlocal calls
        calls += 1
        return ModelResponse(parts=[ToolCallPart("work", {})], usage=RequestUsage(input_tokens=100, output_tokens=20))

    solver = make_solver(tmp_path, monkeypatch, respond, work=work, budget=0.0001)
    try:
        result = await solver.run_until_done_or_gave_up()
        assert result.status == BUDGET_EXHAUSTED
        assert calls == 1
        assert solver.cost_tracker.by_agent[solver.agent_name].usage.input_tokens == 100
        assert result.cost_usd > 0.0001
    finally:
        await solver.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["budget", "missing_usage"])
async def test_claude_budget_interrupts_and_missing_usage_does_not_hide_result(tmp_path, monkeypatch, mode):
    from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock

    from backend.agents.claude_solver import ClaudeSolver

    monkeypatch.chdir(tmp_path)
    solver = ClaudeSolver("claude-sdk/claude-opus-4-6", str(tmp_path), ChallengeMeta(name="claude"),
                          None, CostTracker(), SimpleNamespace(solver_max_cost_usd=0.0001 if mode == "budget" else 0,
                                                              solver_attempt_timeout_seconds=0))

    class Client:
        queries = 0
        interrupted = False

        async def query(self, _prompt):
            self.queries += 1

        async def interrupt(self):
            self.interrupted = True

        async def receive_response(self):
            if mode == "budget":
                yield AssistantMessage(content=[TextBlock("analysis")], model="claude-opus-4-6", message_id="one",
                                       usage={"input_tokens": 100, "output_tokens": 20})
                pytest.fail("Budget must stop this turn after the paid response")
            yield ResultMessage(subtype="success", duration_ms=0, duration_api_ms=0, is_error=False,
                                num_turns=1, session_id="s", total_cost_usd=None, usage=None,
                                structured_output={"type": "gave_up", "findings_summary": "No result yet"})

    client = Client()
    solver._client = client
    try:
        result = await solver.run_until_done_or_gave_up()
        if mode == "budget":
            assert result.status == BUDGET_EXHAUSTED
            assert client.interrupted
            assert result.cost_usd > 0.0001
            assert (await solver.run_until_done_or_gave_up()).status == BUDGET_EXHAUSTED
            assert client.queries == 1
        else:
            assert result.status == GAVE_UP
            assert result.findings_summary == "No result yet"
            assert not solver.cost_tracker.by_agent
    finally:
        solver.tracer.close()


@pytest.mark.asyncio
async def test_codex_budget_uses_current_notification_and_prevents_another_turn(tmp_path, monkeypatch):
    from backend.agents.codex_solver import CodexSolver

    monkeypatch.chdir(tmp_path)
    solver = CodexSolver("codex/gpt-5.4-mini", str(tmp_path), ChallengeMeta(name="codex"), None,
                         CostTracker(), SimpleNamespace(solver_max_cost_usd=0.0001, solver_attempt_timeout_seconds=0))
    stream = asyncio.StreamReader()
    event = {"method": "thread/tokenUsage/updated", "params": {"threadId": "s", "tokenUsage": {
        "total": {"inputTokens": 100, "outputTokens": 20, "cachedInputTokens": 0},
    }}}
    stream.feed_data(json.dumps(event).encode() + b"\n")
    stream.feed_eof()
    solver._proc = SimpleNamespace(stdout=stream)
    solver._thread_id = "s"
    queries = []

    async def rpc(method, params):
        queries.append(method)
        await solver._read_loop()
        return {}

    solver._rpc = rpc
    try:
        result = await solver.run_until_done_or_gave_up()
        assert result.status == BUDGET_EXHAUSTED
        assert result.cost_usd > 0.0001
        assert (await solver.run_until_done_or_gave_up()).status == BUDGET_EXHAUSTED
        assert queries == ["turn/start"]
    finally:
        solver.tracer.close()
