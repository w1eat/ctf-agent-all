"""Record every completed model request, including requests in failed runs."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models import ModelRequestContext
from pydantic_ai.usage import RunUsage

from backend.cost_tracker import CostTracker

_usage_context: ContextVar[tuple[CostTracker, str] | None] = ContextVar("model_usage_accounting", default=None)


@contextmanager
def usage_accounting(tracker: CostTracker | None, agent_name: str):
    """Share accounting through async tasks without putting it in model prompts."""
    token = _usage_context.set((tracker or CostTracker(), agent_name))
    try:
        yield
    finally:
        _usage_context.reset(token)


def current_usage_accounting(model_spec: str) -> tuple[CostTracker, str]:
    return _usage_context.get() or (CostTracker(), f"writeup:{model_spec}")


class CostBudgetExceededError(RuntimeError):
    """The already observed cost reached the configured solver budget."""


@dataclass
class ModelUsageMonitor(AbstractCapability[Any]):
    tracker: CostTracker
    agent_name: str
    model_name: str
    provider: str
    category: str = "solver"
    max_cost_usd: float = 0.0
    tracer: Any = None
    step_counter: list[int] = field(default_factory=lambda: [0])
    recorded: RunUsage = field(default_factory=RunUsage)
    started: float = field(default_factory=time.monotonic)

    async def before_model_request(self, ctx: RunContext[Any], request_context: ModelRequestContext) -> ModelRequestContext:
        usage = self.tracker.by_agent.get(self.agent_name)
        if self.max_cost_usd and usage and usage.cost_usd >= self.max_cost_usd:
            raise CostBudgetExceededError(f"Cost budget exhausted at ${usage.cost_usd:.4f} (limit ${self.max_cost_usd:g})")
        if self.tracer:
            self.tracer.event("model_request", step=self.step_counter[0])
        return request_context

    async def after_model_request(
        self, ctx: RunContext[Any], *, request_context: ModelRequestContext, response: ModelResponse,
    ) -> ModelResponse:
        usage = RunUsage(requests=1)
        usage.incr(response.usage)
        self.tracker.record(self.agent_name, usage, self.model_name, self.provider,
                            category=self.category, request_at=response.timestamp)
        self.recorded.incr(usage)
        if self.tracer:
            self.tracer.model_response(
                " ".join(p.content for p in response.parts if isinstance(p, TextPart)),
                self.step_counter[0], input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
            )
        return response

    def finish(self, usage: Any) -> None:
        """Reconcile partial SDK usage and elapsed time exactly once, before returning a result."""
        if not isinstance(usage, RunUsage):
            usage = RunUsage(**{
                name: getattr(usage, name, 0) for name in (
                    "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "requests", "tool_calls",
                )
            })
        remaining = usage - self.recorded
        if remaining.input_tokens > 0 or remaining.output_tokens > 0 or remaining.cache_read_tokens > 0:
            self.tracker.record(self.agent_name, remaining, self.model_name, self.provider, category=self.category)
        agent = self.tracker.by_agent.get(self.agent_name)
        if agent:
            agent.duration_seconds += time.monotonic() - self.started
            if self.tracer:
                self.tracer.usage(usage.input_tokens, usage.output_tokens, usage.cache_read_tokens, agent.cost_usd)

