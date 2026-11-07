"""Per-agent cost tracking using genai-prices."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from genai_prices import calc_price
from pydantic_ai.usage import RunUsage

logger = logging.getLogger(__name__)

# Provider ID mapping for genai-prices
PROVIDER_MAP: dict[str, str] = {
    "openai": "openai",
    "bedrock": "anthropic",
    "claude-sdk": "anthropic",
    "azure": "openai",
    "deepseek": "deepseek",
    "zen": "openai",
    "codex": "openai",
    "google": "google",
}

# Official standard API estimates, checked 2026-10-23. These override the
# bundled genai-prices snapshot. Sources and billing assumptions: docs/model-pricing.md.
FALLBACK_PRICING: dict[str, dict[str, float]] = {
    "us.anthropic.claude-opus-4-6-v1": {
        # US geographic endpoint: 10% above global Claude rates.
        "input": 5.50,
        "cached_input": 0.55,
        "output": 27.50,
        "cache_write": 6.875,
        "cache_write_1h": 11.00,
    },
    "claude-opus-4-6": {
        "input": 5.00,
        "cached_input": 0.50,
        "output": 25.00,
        "cache_write": 6.25,
        "cache_write_1h": 10.00,
    },
    "gpt-5.4-mini": {
        "input": 0.75,
        "cached_input": 0.075,
        "output": 4.50,
    },
    "gpt-5.4": {
        "input": 2.50,
        "cached_input": 0.25,
        "output": 15.00,
    },
    "gpt-5.3-codex": {
        "input": 1.75,
        "cached_input": 0.175,
        "output": 14.00,
    },
    "gemini-3-flash-preview": {
        "input": 0.50,
        "cached_input": 0.05,
        "output": 3.00,
        "audio_input": 1.00,
        "cached_audio_input": 0.10,
    },
    # DeepSeek Flash peak rates (per 1M tokens). genai-prices may lag behind
    # newly introduced official model IDs, so keep a conservative fallback.
    "deepseek-flash": {
        "input": 0.30,
        "cached_input": 0.006,
        "output": 1.20,
    },
    "deepseek-v4-pro": {"input": 1.32, "cached_input": 0.044, "output": 3.96},
}
for _alias in ("deepseek-v4-flash", "deepseek-v4-flash-vision-exp"):
    FALLBACK_PRICING[_alias] = FALLBACK_PRICING["deepseek-flash"]

# No public API token tariff: do not use a guessed or stale library price.
UNPRICED_MODELS = {"gpt-5.3-codex-spark"}


def _calc_fallback_cost(
    usage: RunUsage, model: str, request_at: datetime | None = None,
) -> float | None:
    pricing = FALLBACK_PRICING.get(model)
    if not pricing:
        return None
    input_rate = pricing.get("input", 0)
    cached_rate = pricing.get("cached_input", input_rate)
    output_rate = pricing.get("output", 0)
    read = min(usage.input_tokens, usage.cache_read_tokens)
    written = min(max(0, usage.input_tokens - read), usage.cache_write_tokens)
    uncached = max(0, usage.input_tokens - read - written)
    long_context = model == "gpt-5.4" and usage.details.get("pricing_input_tokens", usage.input_tokens) > 272_000
    input_multiplier = 2 if long_context else 1
    output_multiplier = 1.5 if long_context else 1
    write_1h = min(written, usage.details.get("cache_creation_1h_input_tokens", 0))
    audio = min(uncached, usage.input_audio_tokens)
    cached_audio = min(read, usage.cache_audio_read_tokens)
    discount = 1.0
    if model.startswith("deepseek-") and request_at is not None:
        utc = request_at.replace(tzinfo=UTC) if request_at.tzinfo is None else request_at.astimezone(UTC)
        if utc.weekday() >= 5 or not (1 <= utc.hour < 4 or 6 <= utc.hour < 10):
            discount = 0.5
        # Weekday public holidays remain conservatively estimated at peak rates.
    return (
        ((uncached - audio) * input_rate + audio * pricing.get("audio_input", input_rate)
         + (read - cached_audio) * cached_rate
         + cached_audio * pricing.get("cached_audio_input", cached_rate)
         + (written - write_1h) * pricing.get("cache_write", input_rate)
         + write_1h * pricing.get("cache_write_1h", input_rate)) * input_multiplier
        + usage.output_tokens * output_rate * output_multiplier
    ) / 1_000_000 * discount


def calc_cost(
    usage: RunUsage, model_name: str, provider_spec: str = "", *, request_at: datetime | None = None,
) -> float | None:
    """Estimate API token cost; None means unavailable, never free usage."""
    if not usage.has_values():
        return 0.0

    if model_name in UNPRICED_MODELS:
        return None
    fallback = _calc_fallback_cost(usage, model_name, request_at)
    if fallback is not None:
        return fallback

    provider_id = PROVIDER_MAP.get(provider_spec, "unknown")

    try:
        price = calc_price(usage, model_name, provider_id=provider_id)
        return float(price.total_price)
    except Exception:
        pass

    return None


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _cache_rate(usage: RunUsage) -> str:
    """Compute cache hit rate as a percentage string."""
    if usage.input_tokens == 0:
        return "n/a"
    rate = (usage.cache_read_tokens / usage.input_tokens) * 100
    return f"{rate:.0f}%"


@dataclass
class AgentUsage:
    usage: RunUsage = field(default_factory=RunUsage)
    model_name: str = ""
    provider_spec: str = ""
    duration_seconds: float = 0.0
    cost_usd: float = 0.0
    category: str = "solver"
    unknown_price_requests: int = 0
    estimated_cost_usd: float = 0.0
    reported_cost_usd: float = 0.0


@dataclass
class CostTracker:
    by_agent: dict[str, AgentUsage] = field(default_factory=dict)

    def record_tokens(
        self,
        agent_name: str,
        model_name: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0,
        provider_spec: str = "",
        duration_seconds: float = 0.0,
        *,
        cache_write_tokens: int = 0,
        details: dict[str, int] | None = None,
        reported_cost_usd: float | None = None,
        category: str = "solver",
    ) -> None:
        """Record token usage without requiring pydantic_ai.RunUsage."""
        usage = RunUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read_tokens,
            cache_write_tokens=cache_write_tokens,
            details=details or {},
        )
        self.record(agent_name, usage, model_name, provider_spec, duration_seconds,
                    reported_cost_usd=reported_cost_usd, category=category)

    def record(
        self,
        agent_name: str,
        usage: RunUsage,
        model_name: str,
        provider_spec: str = "",
        duration_seconds: float = 0.0,
        *,
        reported_cost_usd: float | None = None,
        category: str = "solver",
        request_at: datetime | None = None,
    ) -> None:
        reported = reported_cost_usd is not None and math.isfinite(reported_cost_usd) and reported_cost_usd >= 0
        cost = reported_cost_usd if reported else calc_cost(usage, model_name, provider_spec, request_at=request_at)

        if agent_name not in self.by_agent:
            self.by_agent[agent_name] = AgentUsage(
                model_name=model_name, provider_spec=provider_spec, category=category,
            )

        agent = self.by_agent[agent_name]
        agent.usage += usage
        agent.duration_seconds += duration_seconds
        if cost is None:
            if agent.unknown_price_requests == 0:
                logger.warning("Price unavailable for %s; tokens retained, cost total is incomplete", model_name)
            agent.unknown_price_requests += max(1, usage.requests)
        else:
            agent.cost_usd += cost
            if reported:
                agent.reported_cost_usd += cost
            else:
                agent.estimated_cost_usd += cost

        # Log per-step with cache rate (f-string avoids Rich handler % formatting issues)
        logger.debug(
            f"{agent_name}: {_fmt_tokens(usage.input_tokens)} in / "
            f"{_fmt_tokens(usage.cache_read_tokens)} cached ({_cache_rate(usage)} hit) / "
            f"{_fmt_tokens(usage.output_tokens)} out | "
            f"{'price unavailable' if cost is None else f'${cost:.4f}'} | {duration_seconds:.1f}s"
        )

    @property
    def total_cost_usd(self) -> float:
        return sum(a.cost_usd for a in self.by_agent.values())

    @property
    def total_tokens(self) -> int:
        total = RunUsage()
        for a in self.by_agent.values():
            total += a.usage
        return total.total_tokens

    @property
    def unknown_price_requests(self) -> int:
        return sum(a.unknown_price_requests for a in self.by_agent.values())

    def get_usage_by_category(self) -> dict[str, dict[str, Any]]:
        groups: dict[str, dict[str, Any]] = {}
        for agent in self.by_agent.values():
            group = groups.setdefault(agent.category, {
                "cost_usd": 0.0, "tokens": 0, "unknown_price_requests": 0,
                "estimated_cost_usd": 0.0, "reported_cost_usd": 0.0,
            })
            group["cost_usd"] += agent.cost_usd
            group["tokens"] += agent.usage.total_tokens
            group["unknown_price_requests"] += agent.unknown_price_requests
            group["estimated_cost_usd"] += agent.estimated_cost_usd
            group["reported_cost_usd"] += agent.reported_cost_usd
        return groups

    def reconcile_reported_cost(
        self, agent_name: str, model_name: str, estimated: float, reported: float, category: str = "solver",
    ) -> None:
        """Replace this turn's local estimate with the SDK's reported delta."""
        agent = self.by_agent.setdefault(agent_name, AgentUsage(model_name=model_name, provider_spec="claude-sdk", category=category))
        agent.cost_usd += reported - estimated
        agent.estimated_cost_usd -= estimated
        agent.reported_cost_usd += reported

    def format_usage(self, agent_name: str) -> str:
        """Format: '45k in / 32k cached (71% hit) / 2.1k out | $0.05 | 28.3s'"""
        agent = self.by_agent.get(agent_name)
        if not agent:
            return ""
        u = agent.usage
        return (
            f"{_fmt_tokens(u.input_tokens)} in / "
            f"{_fmt_tokens(u.cache_read_tokens)} cached ({_cache_rate(u)} hit) / "
            f"{_fmt_tokens(u.output_tokens)} out | "
            f"${agent.cost_usd:.2f}{' + price unavailable' if agent.unknown_price_requests else ''} | "
            f"{agent.duration_seconds:.1f}s"
        )

    def get_usage_by_model(self) -> dict[str, dict[str, Any]]:
        by_model: dict[str, dict[str, Any]] = {}
        for agent in self.by_agent.values():
            model = agent.model_name
            if model not in by_model:
                by_model[model] = {"cost": 0.0, "input": 0, "cached": 0, "output": 0}
            by_model[model]["cost"] += agent.cost_usd
            by_model[model]["input"] += agent.usage.input_tokens
            by_model[model]["cached"] += agent.usage.cache_read_tokens
            by_model[model]["output"] += agent.usage.output_tokens
        return by_model

    def log_summary(self) -> None:
        """Log summary grouped by model with cache hit rates."""
        for category, usage in self.get_usage_by_category().items():
            logger.info("  %s: $%.4f | %s tokens | %s unpriced requests",
                        category, usage["cost_usd"], _fmt_tokens(usage["tokens"]), usage["unknown_price_requests"])
        by_model = self.get_usage_by_model()
        for model, s in by_model.items():
            hit_rate = f"{(s['cached'] / s['input'] * 100):.0f}%" if s["input"] > 0 else "n/a"
            logger.info(
                "  %s: $%.2f | %s in / %s cached (%s hit) / %s out",
                model, s["cost"],
                _fmt_tokens(s["input"]),
                _fmt_tokens(s["cached"]),
                hit_rate,
                _fmt_tokens(s["output"]),
            )
        total = sum(s["input"] for s in by_model.values())
        total_cached = sum(s["cached"] for s in by_model.values())
        overall_hit = f"{(total_cached / total * 100):.0f}%" if total > 0 else "n/a"
        logger.info(
            "  Total: $%.2f | %s tokens | %s overall cache hit rate",
            self.total_cost_usd,
            _fmt_tokens(self.total_tokens),
            overall_hit,
        )
        if self.unknown_price_requests:
            logger.warning("Total cost is incomplete: %s requests have no known price", self.unknown_price_requests)
