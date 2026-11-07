from types import SimpleNamespace

import pytest

from backend.cost_tracker import CostTracker
from backend.sdk_usage import ClaudeUsage, CodexUsage


def test_claude_partial_response_is_counted_once_even_without_final_result():
    tracker = CostTracker()
    ledger = ClaudeUsage(tracker, "agent", "claude-opus-4-6")
    message = SimpleNamespace(message_id="one", usage={"input_tokens": 10, "output_tokens": 5,
                                                      "cache_read_input_tokens": 20, "cache_creation_input_tokens": 30})
    ledger.observe(message)
    ledger.observe(message)
    ledger.finish()
    assert tracker.total_tokens == 65
    assert tracker.by_agent["agent"].usage.cache_write_tokens == 30
    assert tracker.total_cost_usd > 0


def test_claude_one_hour_cache_and_stale_snapshots_keep_correct_cost():
    tracker = CostTracker()
    ledger = ClaudeUsage(tracker, "agent", "claude-opus-4-6")
    for written in (100, 80, 100):
        ledger.observe(SimpleNamespace(message_id="same-response", usage={
            "cache_creation_input_tokens": written,
            "cache_creation": {"ephemeral_1h_input_tokens": written},
        }))
    assert tracker.total_tokens == 100
    assert tracker.total_cost_usd == pytest.approx(100 * 10 / 1_000_000)


def test_claude_missing_result_usage_is_not_invented():
    tracker = CostTracker()
    ledger = ClaudeUsage(tracker, "agent", "claude-opus-4-6")
    assert ledger.result(SimpleNamespace(session_id="s", total_cost_usd=None, usage=None)) is None
    ledger.finish()
    assert not tracker.by_agent


def test_claude_zeroed_crash_result_keeps_observed_cost_and_previous_session_total():
    tracker = CostTracker()
    ledger = ClaudeUsage(tracker, "agent", "claude-opus-4-6")
    ledger.result(SimpleNamespace(session_id="s", total_cost_usd=0.1, usage={}))
    ledger.begin_turn()
    ledger.observe(SimpleNamespace(message_id="paid", usage={"input_tokens": 100, "output_tokens": 20}))
    ledger.result(SimpleNamespace(session_id="s", total_cost_usd=0.0, usage={}))
    assert tracker.total_cost_usd == pytest.approx(0.101)
    assert tracker.total_tokens == 120
    ledger.begin_turn()
    ledger.result(SimpleNamespace(session_id="s", total_cost_usd=0.12, usage={}))
    assert tracker.total_cost_usd == pytest.approx(0.121)


def test_claude_result_reconciles_tokens_and_cumulative_sdk_cost_without_double_counting():
    tracker = CostTracker()
    ledger = ClaudeUsage(tracker, "coordinator", "claude-opus-4-6", "coordinator")
    ledger.observe(SimpleNamespace(message_id="one", usage={"input_tokens": 10, "output_tokens": 5}))
    ledger.result(SimpleNamespace(session_id="s", total_cost_usd=0.1, usage={"input_tokens": 15, "output_tokens": 10}))
    ledger.finish()
    assert tracker.total_tokens == 25
    assert tracker.total_cost_usd == pytest.approx(0.1)
    ledger.begin_turn()
    ledger.result(SimpleNamespace(session_id="s", total_cost_usd=0.13, usage={"input_tokens": 20, "output_tokens": 10}))
    assert tracker.total_tokens == 55
    assert tracker.total_cost_usd == pytest.approx(0.13)
    assert tracker.by_agent["coordinator"].reported_cost_usd == pytest.approx(0.13)
    assert tracker.by_agent["coordinator"].estimated_cost_usd == pytest.approx(0)
    ledger.begin_turn()
    ledger.result(SimpleNamespace(session_id="new-session", total_cost_usd=0.02, usage={}))
    assert tracker.total_cost_usd == pytest.approx(0.15)


def test_codex_repeated_and_out_of_order_total_notifications_do_not_double_count():
    tracker = CostTracker()
    ledger = CodexUsage(tracker, "writer", "gpt-5.4-mini", "writeup")
    def event(input_tokens, output_tokens, thread="one"):
        return {"threadId": thread, "tokenUsage": {"total": {
            "inputTokens": input_tokens, "outputTokens": output_tokens, "cachedInputTokens": input_tokens // 2,
        }}}
    for message in [event(100, 20), event(100, 20), event(80, 10), event(200, 40), event(30, 10, "two")]:
        ledger.observe(message)
    assert tracker.total_tokens == 280
    assert tracker.by_agent["writer"].usage.cache_read_tokens == 115
    assert tracker.get_usage_by_category()["writeup"]["tokens"] == 280

