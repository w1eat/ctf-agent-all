"""Account for SDK response snapshots without counting cumulative totals twice."""

from __future__ import annotations

import math
import time
from typing import Any

from pydantic_ai.usage import RunUsage

from backend.cost_tracker import CostTracker

_TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")


def _positive_delta(current: RunUsage, previous: RunUsage) -> RunUsage:
    return RunUsage(**{name: max(0, getattr(current, name) - getattr(previous, name)) for name in _TOKEN_FIELDS},
                    details={name: max(0, current.details.get(name, 0) - previous.details.get(name, 0))
                             for name in current.details | previous.details})


def _claude_usage(raw: Any) -> RunUsage:
    if not isinstance(raw, dict):
        return RunUsage()
    read = raw.get("cache_read_input_tokens", raw.get("cache_read_tokens", 0)) or 0
    written = raw.get("cache_creation_input_tokens", 0) or 0
    creation = raw.get("cache_creation") or {}
    return RunUsage(input_tokens=(raw.get("input_tokens", 0) or 0) + read + written,
                    output_tokens=raw.get("output_tokens", 0) or 0,
                    cache_read_tokens=read, cache_write_tokens=written,
                    details={"cache_creation_1h_input_tokens": creation.get("ephemeral_1h_input_tokens", 0)})


class ClaudeUsage:
    """Assistant usage survives a failed turn; a result reconciles SDK cost estimates."""

    def __init__(self, tracker: CostTracker, agent_name: str, model: str, category: str = "solver") -> None:
        self.tracker, self.agent_name, self.model, self.category = tracker, agent_name, model, category
        self._cost_totals: dict[str, float] = {}
        self.begin_turn()

    def begin_turn(self) -> None:
        self._messages: dict[str, RunUsage] = {}
        self._recorded = RunUsage()
        self._estimated = 0.0
        self._started = time.monotonic()

    def _record(self, usage: RunUsage) -> None:
        if not usage.input_tokens and not usage.output_tokens:
            return
        before = self.tracker.by_agent.get(self.agent_name)
        estimated_before = before.estimated_cost_usd if before else 0.0
        self.tracker.record(self.agent_name, usage, self.model, "claude-sdk", category=self.category)
        self._estimated += self.tracker.by_agent[self.agent_name].estimated_cost_usd - estimated_before
        self._recorded.incr(usage)

    def observe(self, message: Any) -> None:
        message_id = getattr(message, "message_id", None)
        if not message_id or not isinstance(getattr(message, "usage", None), dict):
            return  # A result can still provide turn totals when per-message usage is unavailable.
        current = _claude_usage(message.usage)
        previous = self._messages.get(message_id, RunUsage())
        self._record(_positive_delta(current, previous))
        self._messages[message_id] = RunUsage(
            **{name: max(getattr(current, name), getattr(previous, name)) for name in _TOKEN_FIELDS},
            details={name: max(current.details.get(name, 0), previous.details.get(name, 0))
                     for name in current.details | previous.details},
        )

    def result(self, message: Any) -> float | None:
        total = _claude_usage(getattr(message, "usage", None))
        self._record(_positive_delta(total, self._recorded))
        reported = getattr(message, "total_cost_usd", None)
        if isinstance(reported, (int, float)) and math.isfinite(reported) and reported >= 0:
            session = str(getattr(message, "session_id", "") or "default")
            previous = self._cost_totals.get(session, 0.0)
            if reported < previous:
                return self._estimated or None  # A crash may zero the SDK's session total.
            delta = reported - previous
            self._cost_totals[session] = reported
            if not delta and self._recorded.total_tokens:
                return self._estimated or None  # A zeroed result must not erase paid responses.
            self.tracker.reconcile_reported_cost(self.agent_name, self.model, self._estimated, delta, self.category)
            return delta
        return None

    def finish(self) -> None:
        agent = self.tracker.by_agent.get(self.agent_name)
        if agent:
            agent.duration_seconds += time.monotonic() - self._started


class CodexUsage:
    def __init__(self, tracker: CostTracker, agent_name: str, model: str, category: str = "solver") -> None:
        self.tracker, self.agent_name, self.model, self.category = tracker, agent_name, model, category
        self._totals: dict[str, RunUsage] = {}

    def observe(self, params: dict[str, Any]) -> None:
        token_usage = params.get("tokenUsage") or {}
        total = token_usage.get("total") or {}
        if not total:
            return
        scope = str(params.get("threadId") or "default")
        current = RunUsage(input_tokens=total.get("inputTokens", 0), output_tokens=total.get("outputTokens", 0),
                           cache_read_tokens=total.get("cachedInputTokens", 0))
        previous = self._totals.get(scope, RunUsage())
        delta = _positive_delta(current, previous)
        if delta.input_tokens or delta.output_tokens:
            delta.details["pricing_input_tokens"] = (token_usage.get("last") or {}).get("inputTokens", delta.input_tokens)
            self.tracker.record(self.agent_name, delta, self.model, "codex", category=self.category)
        self._totals[scope] = RunUsage(**{name: max(getattr(current, name), getattr(previous, name)) for name in _TOKEN_FIELDS})
