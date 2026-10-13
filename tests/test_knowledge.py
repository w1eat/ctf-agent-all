import asyncio
import shutil
from types import SimpleNamespace

from backend.knowledge import KnowledgeQuery, KnowledgeStore, record_from_result
from backend.knowledge_service import KnowledgeQueryBudget, KnowledgeService
from backend.prompts import ChallengeMeta
from backend.solver_base import FLAG_FOUND, SolverResult


def test_query_budget_reports_exhaustion_separately_from_no_hits():
    class EmptySearch:
        async def search_async(self, query, **kwargs):
            return []

    budget = KnowledgeQueryBudget(EmptySearch(), max_queries=1)
    assert asyncio.run(budget.search_async("PostgreSQL")) == []
    exhausted = asyncio.run(budget.search_async("boolean oracle"))
    assert exhausted == []
    assert exhausted.errors == ("query_budget_exhausted",)


def test_missing_pinned_snapshot_is_reported_as_error_not_empty_search(tmp_path):
    settings = SimpleNamespace(external_knowledge_enabled=False, challenge_run_id="",
                               external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3", enabled=False),
                               local_root=tmp_path / "local-index")
    service.local.snapshot_id = "pinned-local-v2"
    service.local.available = False

    hits = service.search("PostgreSQL")
    assert hits == []
    assert hits.errors == ("pinned-local-v2:snapshot_unavailable",)
    assert service.initial_context(KnowledgeQuery(name="PostgreSQL")) == ""
    assert service.initial_context_audit["errors"] == ["pinned-local-v2:snapshot_unavailable"]


def test_knowledge_redacts_flag_and_retrieves_persisted_method(tmp_path):
    meta = ChallengeMeta(
        name="demo-pwn",
        category="pwn",
        challenge_mode="attachment",
        description="A stack overflow challenge",
    )
    flag = "moectf{secret-value}"
    result = SolverResult(
        flag=flag,
        status=FLAG_FOUND,
        findings_summary=(
            "Flag found via measured the RIP offset with cyclic and used a ret2win payload: "
            f"{flag}"
        ),
        step_count=4,
        cost_usd=0.1,
        log_path="trace.jsonl",
    )
    record = record_from_result(meta, result, "deepseek/deepseek-flash", confirmed=True)
    assert record is not None
    assert flag not in record.method
    assert flag not in record.reasoning

    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    assert store.remember(record) is True
    assert store.remember(record) is False

    context = store.render_context(KnowledgeQuery.from_meta(meta))
    assert "cyclic" in context
    assert flag not in context
    assert "accepted" in context


def test_unverified_candidate_is_not_marked_accepted(tmp_path):
    meta = ChallengeMeta(name="demo", category="web")
    result = SolverResult(
        flag="CTF{guess}",
        status=FLAG_FOUND,
        findings_summary="Flag found via found a reflected parameter: CTF{guess}",
        step_count=1,
        cost_usd=0.0,
        log_path="trace.jsonl",
    )
    record = record_from_result(meta, result, "model", confirmed=False)
    assert record is not None
    assert record.outcome == "unverified_candidate"


def test_knowledge_store_releases_sqlite_file_on_windows(tmp_path):
    root = tmp_path / "disposable-knowledge"
    KnowledgeStore(root / "knowledge.sqlite3")
    shutil.rmtree(root)
    assert not root.exists()
