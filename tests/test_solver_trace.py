from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from backend.agents.solver import TracingToolset
from backend.tracing import SolverTracer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("display", "confirmed_flag", "expected"),
    [
        ("INCORRECT — already tried this exact flag.", None, False),
        ("submit_flag error: No submit recipe is available", None, False),
        ("SUBMISSION_PENDING — inspect browser evidence", None, False),
        ("ALREADY SOLVED — a different flag was confirmed", "FLAG{other}", False),
        ("CORRECT — Agent confirmed", "FLAG{ok}", True),
    ],
)
async def test_trace_only_marks_exact_confirmed_submission(display, confirmed_flag, expected):
    async def call_tool(*_args):
        return display

    events = []
    tracer = SimpleNamespace(
        tool_call=lambda *_args: None,
        tool_result=lambda *_args: None,
        event=lambda *args, **_kwargs: events.append(args[0]),
    )
    toolset = TracingToolset(
        wrapped=SimpleNamespace(call_tool=call_tool),
        tracer=tracer,
        loop_detector=SimpleNamespace(check=lambda *_args: None),
        step_counter=[0],
    )
    ctx = SimpleNamespace(deps=SimpleNamespace(confirmed_flag=confirmed_flag, message_bus=None))

    assert await toolset.call_tool("submit_flag", {"flag": "FLAG{ok}"}, ctx, None) == display
    assert ("flag_confirmed" in events) is expected


def test_knowledge_trace_records_metadata_without_document_body(tmp_path):
    tracer = SolverTracer("demo", "model", log_dir=str(tmp_path))
    tracer.knowledge_snapshots = {"external": "upstream-v5", "local": "local-v1"}
    tracer.tool_call("search_knowledge", {"query": "PostgreSQL boolean oracle"}, 1)
    tracer.tool_result("search_knowledge", json.dumps([{"document_id": "local:card",
        "snippet": "PRIVATE KNOWLEDGE BODY", "source": "local-curated"}]), 1)
    tracer.tool_call("read_knowledge", {"document_id": "local:card"}, 2)
    tracer.tool_result("read_knowledge", json.dumps({"document_id": "local:card",
        "snapshot_id": "local-v1", "text": "PRIVATE KNOWLEDGE BODY"}), 2)
    tracer.close()
    events = [json.loads(line) for line in next(tmp_path.glob("*.jsonl")).read_text().splitlines()]
    assert "PRIVATE KNOWLEDGE BODY" not in json.dumps(events)
    search = next(event for event in events if event["type"] == "knowledge_search")
    assert search["keywords"] == "postgresql boolean oracle"
    assert search["document_ids"] == ["local:card"]
    assert search["local_snapshot"] == "local-v1"


def test_interleaved_knowledge_searches_keep_their_own_keywords(tmp_path):
    tracer = SolverTracer("demo", "model", log_dir=str(tmp_path))
    tracer.tool_call("search_knowledge", {"query": "PostgreSQL boolean"}, 1)
    tracer.tool_call("search_knowledge", {"query": "COPY TO PROGRAM"}, 2)
    tracer.tool_result("search_knowledge", "[]", 2)
    tracer.tool_result("search_knowledge", "[]", 1)
    tracer.close()

    events = [json.loads(line) for line in next(tmp_path.glob("*.jsonl")).read_text().splitlines()]
    searches = {event["step"]: event for event in events if event["type"] == "knowledge_search"}
    assert searches[1]["keywords"] == "postgresql boolean"
    assert searches[2]["keywords"] == "copy to program"
