from datetime import UTC, datetime

import pytest
from pydantic_ai.usage import RunUsage

from backend.cost_tracker import CostTracker, calc_cost


@pytest.mark.parametrize(("model", "input_rate", "cached_rate", "output_rate"), [
    ("deepseek-flash", 0.30, 0.006, 1.20),
    ("deepseek-v4-flash", 0.30, 0.006, 1.20),
    ("deepseek-v4-pro", 1.32, 0.044, 3.96),
    ("gemini-3-flash-preview", 0.50, 0.05, 3.00),
    ("gpt-5.4-mini", 0.75, 0.075, 4.50),
    ("gpt-5.4", 2.50, 0.25, 15.00),
    ("gpt-5.3-codex", 1.75, 0.175, 14.00),
    ("claude-opus-4-6", 5.00, 0.50, 25.00),
    ("us.anthropic.claude-opus-4-6-v1", 5.50, 0.55, 27.50),
])
def test_verified_rates_override_bundled_library(monkeypatch, model, input_rate, cached_rate, output_rate):
    def stale_price(*_args, **_kwargs):
        pytest.fail("Verified models must not use a stale library snapshot")

    monkeypatch.setattr("backend.cost_tracker.calc_price", stale_price)
    usage = RunUsage(input_tokens=100_000, cache_read_tokens=40_000, output_tokens=20_000)
    assert calc_cost(usage, model) == pytest.approx(input_rate * 0.06 + cached_rate * 0.04 + output_rate * 0.02)


@pytest.mark.parametrize(("at", "factor"), [
    (datetime(2026, 10, 23, 1, tzinfo=UTC), 1),
    (datetime(2026, 10, 23, 4, tzinfo=UTC), 0.5),
    (datetime(2026, 10, 23, 6, tzinfo=UTC), 1),
    (datetime(2026, 10, 23, 10, tzinfo=UTC), 0.5),
    (datetime(2026, 10, 24, 2, tzinfo=UTC), 0.5),
])
def test_deepseek_peak_and_off_peak_boundaries(at, factor):
    usage = RunUsage(input_tokens=1_000_000, output_tokens=1_000_000)
    assert calc_cost(usage, "deepseek-flash", request_at=at) == pytest.approx(1.5 * factor)


def test_long_context_is_priced_per_request_not_aggregate():
    usage = RunUsage(input_tokens=300_000, cache_read_tokens=100_000, output_tokens=10_000)
    assert calc_cost(usage, "gpt-5.4") == pytest.approx(0.2 * 5 + 0.1 * 0.5 + 0.01 * 22.5)
    usage.details["pricing_input_tokens"] = 150_000
    assert calc_cost(usage, "gpt-5.4") == pytest.approx(0.2 * 2.5 + 0.1 * 0.25 + 0.01 * 15)


def test_claude_cache_creation_and_reads_are_not_charged_as_regular_input():
    usage = RunUsage(input_tokens=300_000, cache_read_tokens=100_000, cache_write_tokens=100_000,
                     details={"cache_creation_1h_input_tokens": 40_000})
    assert calc_cost(usage, "claude-opus-4-6") == pytest.approx(0.1 * 5 + 0.1 * 0.5 + 0.06 * 6.25 + 0.04 * 10)


def test_gemini_audio_and_cached_audio_have_distinct_rates():
    usage = RunUsage(input_tokens=1000, input_audio_tokens=400, cache_read_tokens=200, cache_audio_read_tokens=100)
    assert calc_cost(usage, "gemini-3-flash-preview") == pytest.approx((400 * 0.5 + 400 * 1 + 100 * 0.05 + 100 * 0.1) / 1_000_000)


def test_unknown_price_is_exposed_and_does_not_erase_tokens(monkeypatch):
    def missing(*_args, **_kwargs):
        raise LookupError("unknown")

    monkeypatch.setattr("backend.cost_tracker.calc_price", missing)
    tracker = CostTracker()
    tracker.record_tokens("solver", "not-a-priced-model", input_tokens=10, output_tokens=20)
    assert calc_cost(RunUsage(input_tokens=1), "gpt-5.3-codex-spark", "codex") is None
    assert tracker.total_tokens == 30
    assert tracker.unknown_price_requests == 1
    assert "price unavailable" in tracker.format_usage("solver")
    assert tracker.get_usage_by_category()["solver"]["unknown_price_requests"] == 1


def test_category_totals_separate_sdk_reports_from_api_estimates():
    tracker = CostTracker()
    tracker.record_tokens("solve", "gpt-5.4-mini", input_tokens=100)
    tracker.record_tokens("coord", "claude-opus-4-6", output_tokens=100, category="coordinator", reported_cost_usd=0.04)
    tracker.record_tokens("write", "deepseek-flash", output_tokens=100, category="writeup")
    groups = tracker.get_usage_by_category()
    assert set(groups) == {"solver", "coordinator", "writeup"}
    assert groups["coordinator"]["reported_cost_usd"] == 0.04
    assert groups["solver"]["estimated_cost_usd"] > 0
    assert tracker.total_cost_usd == pytest.approx(sum(group["cost_usd"] for group in groups.values()))

