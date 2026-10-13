"""Offline curated corpus, immutable reads, review gates, and model adapters."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

import backend.local_knowledge as local_module
from backend.external_knowledge import ExternalKnowledge
from backend.knowledge import KnowledgeStore
from backend.knowledge_service import (
    KnowledgeQueryBudget,
    KnowledgeService,
    make_claude_knowledge_server,
)
from backend.local_knowledge import (
    LocalKnowledge,
    approve_draft,
    local_snapshot_for_run,
    normalized_keywords,
    pin_local_snapshot,
    write_verified_draft,
)
from backend.prompts import ChallengeMeta, build_prompt
from backend.solver_base import CANDIDATE_FOUND, VERIFIED, SolverResult
from backend.tools.knowledge import read_knowledge, search_knowledge


def _service(tmp_path: Path, source: Path, root: Path, run_id: str) -> KnowledgeService:
    settings = SimpleNamespace(external_knowledge_enabled=False, challenge_run_id=run_id,
                               external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    return KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3", enabled=False),
                            local_root=root)


def test_local_snapshot_updates_and_old_run_keeps_immutable_document(tmp_path, monkeypatch):
    source, root = tmp_path / "local", tmp_path / "index"
    source.mkdir()
    (source / "postgres.md").write_text("# PostgreSQL\nboolean oracle first version\n", encoding="utf-8")
    (source / "AI-SEARCH-INDEX.md").write_text(
        "### Database\n- [card](postgres.md)\n- **关键词**: `pgsql`\n", encoding="utf-8")
    (source / "ignored.txt").write_text("never index this", encoding="utf-8")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: pytest.fail("network/git is forbidden"))
    first = LocalKnowledge.index(source, root)["snapshot_id"]
    assert pin_local_snapshot("new-run", root) == first
    service = _service(tmp_path, source, root, "new-run")
    hit = service.search("pgsql oracle")[0]
    assert hit["source"] == "local-curated"
    assert hit["path"] == "knowledge/local/postgres.md"
    assert hit["document_id"].startswith("local:")
    assert "first version" in asyncio.run(service.read_async(hit["document_id"]))["text"]
    assert all(item["path"] != "ignored.txt" for item in service.search("never index this"))

    (source / "postgres.md").write_text("# PostgreSQL\nboolean oracle second version\n", encoding="utf-8")
    second = LocalKnowledge.index(source, root)["snapshot_id"]
    assert second != first
    assert local_snapshot_for_run("new-run", root) == first
    assert local_snapshot_for_run("legacy-run", root) == ""
    assert "first version" in asyncio.run(service.read_async(hit["document_id"]))["text"]
    assert pin_local_snapshot("later-run", root) == second
    later = _service(tmp_path, source, root, "later-run")
    assert "second version" in asyncio.run(later.read_async(hit["document_id"]))["text"]
    (root / "snapshots" / first / "source" / "postgres.md").write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        asyncio.run(service.read_async(hit["document_id"]))


def test_ignored_file_changes_diagnostic_snapshot(tmp_path):
    source, root = tmp_path / "local", tmp_path / "index"
    source.mkdir()
    (source / "method.md").write_text("# Method\nPostgreSQL", encoding="utf-8")
    first = LocalKnowledge.index(source, root)["snapshot_id"]
    assert LocalKnowledge(root).status()["diagnostics"] == 0
    (source / "ignored.txt").write_text("not indexed", encoding="utf-8")
    second = LocalKnowledge.index(source, root)["snapshot_id"]
    assert second != first
    assert LocalKnowledge(root).status()["diagnostics"] == 1
    assert not LocalKnowledge(root).search("not indexed")


def test_verification_status_comes_from_fixed_snapshot(tmp_path):
    source, root = tmp_path / "local", tmp_path / "index"
    source.mkdir()
    pending = source / "pending.md"
    pending.write_text("---\nverification_status: pending\n---\n# Pending\npendingmarker\n",
                       encoding="utf-8")
    (source / "verified.md").write_text(
        "---\nverification_status: verified\n---\n# Verified\nverifiedmarker\n",
        encoding="utf-8")
    first = LocalKnowledge.index(source, root)["snapshot_id"]
    pin_local_snapshot("status-run", root)
    service = _service(tmp_path, source, root, "status-run")
    pending_hit = service.search("pendingmarker")[0]
    verified_hit = service.search("verifiedmarker")[0]
    assert pending_hit["verification_status"] == "pending"
    assert verified_hit["verification_status"] == "verified"
    assert asyncio.run(service.read_async(pending_hit["document_id"]))["verification_status"] == "pending"
    assert asyncio.run(service.read_async(verified_hit["document_id"]))["verification_status"] == "verified"

    pending.write_text("---\nverification_status: verified\n---\n# Pending\npendingmarker\n",
                       encoding="utf-8")
    assert service.search("pendingmarker")[0]["verification_status"] == "pending"
    assert asyncio.run(service.read_async(pending_hit["document_id"]))["verification_status"] == "pending"
    assert LocalKnowledge.index(source, root)["snapshot_id"] != first
    pin_local_snapshot("status-later", root)
    later = _service(tmp_path, source, root, "status-later")
    assert later.search("pendingmarker")[0]["verification_status"] == "verified"


def test_normalized_keywords_removes_candidate_values():
    normalized = normalized_keywords(
        "PostgreSQL flag=VERYSECRET123 answer:ANSWERSECRET candidate=CANDIDATESECRET "
        "token=SESSIONSECRET PGPASSWORD=PGSECRET DB_PASSWORD=DBSECRET "
        "postgresql://user:pass@db.example.invalid/app https://challenge.example.invalid/path"
    )
    assert normalized.startswith("postgresql")
    assert all(secret not in normalized for secret in (
        "verysecret123", "answersecret", "candidatesecret", "sessionsecret", "pgsecret",
        "dbsecret", "db.example.invalid", "challenge.example.invalid"
    ))
    assert normalized_keywords("flag=secret PostgreSQL") == "postgresql"


def test_local_related_files_use_local_ids_and_paths(tmp_path):
    source, root = tmp_path / "local", tmp_path / "index"
    folder = source / "工具使用"
    folder.mkdir(parents=True)
    (folder / "one.md").write_text("# One\nPostgreSQL", encoding="utf-8")
    (folder / "two.md").write_text("# Two\nPostgreSQL", encoding="utf-8")
    LocalKnowledge.index(source, root)
    pin_local_snapshot("related-run", root)
    service = _service(tmp_path, source, root, "related-run")
    first_id = next(hit["document_id"] for hit in service.search("One")
                    if hit["path"].endswith("one.md"))
    related = asyncio.run(service.read_async(first_id))["related_files"]
    assert len(related) == 1
    assert related[0]["document_id"].startswith("local:")
    assert related[0]["path"] == "knowledge/local/工具使用/two.md"
    assert "# Two" in asyncio.run(service.read_async(related[0]["document_id"]))["text"]


def test_verified_draft_redacts_and_approval_reindexes(tmp_path):
    inbox, source, root = tmp_path / "inbox", tmp_path / "local", tmp_path / "index"
    source.mkdir()
    meta = ChallengeMeta(name="Validated method", category="web")
    result = SolverResult(
        "FLAG{private}", VERIFIED,
        "PostgreSQL boolean oracle recovered FLAG{private}; Bearer supersecret123; "
        "https://user:pass@example.invalid/path; PGPASSWORD=hunter2; "
        "postgresql://dbuser:dbpass@database.invalid/app",
        4, 0.1, "trace", verified_by=("solver-a", "solver-b"),
        solution_steps=("Check pgsql role membership and cookie: session123",),
    )
    assert write_verified_draft(meta, result, "candidate_found", inbox_dir=inbox) is None
    assert write_verified_draft(meta, SolverResult("FLAG{private}", CANDIDATE_FOUND,
           result.findings_summary, 4, 0.1, "trace", verified_by=("solver-a",)),
           "independent_quorum", inbox_dir=inbox) is None
    draft = write_verified_draft(meta, result, "independent_quorum", run_id="run1", inbox_dir=inbox)
    assert draft is not None
    content = draft.read_text(encoding="utf-8")
    assert "FLAG{private}" not in content
    assert "supersecret123" not in content
    assert "example.invalid" not in content
    assert "session123" not in content
    assert "hunter2" not in content
    assert "database.invalid" not in content
    assert content.count("verification_status: verified") == 1
    approved = approve_draft(draft.name, inbox_dir=inbox, source_dir=source, index_root=root)
    assert not draft.exists()
    assert approved["snapshot_id"] == LocalKnowledge(root).snapshot_id
    assert LocalKnowledge(root).search("PostgreSQL boolean oracle")
    with pytest.raises(ValueError, match="inside knowledge/inbox"):
        approve_draft(source / draft.name, inbox_dir=inbox, source_dir=source, index_root=root)
    unsafe = inbox / "unsafe.md"
    unsafe.write_text("---\nsource_challenge: test\nconfirmation_source: platform_confirmed\n"
                      "verification_status: verified\n---\nFLAG{leak}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="contains a flag"):
        approve_draft(unsafe.name, inbox_dir=inbox, source_dir=source, index_root=root)
    assert unsafe.exists()
    unsafe_pg = inbox / "unsafe-pg.md"
    unsafe_pg.write_text("---\nsource_challenge: test\nconfirmation_source: platform_confirmed\n"
                         "verification_status: verified\n---\nPGPASSWORD=hunter2\n",
                         encoding="utf-8")
    with pytest.raises(ValueError, match="contains a flag"):
        approve_draft(unsafe_pg.name, inbox_dir=inbox, source_dir=source, index_root=root)
    assert unsafe_pg.exists()
    binary = inbox / "binary.md"
    binary.write_bytes(b"---\nsource_challenge: test\nconfirmation_source: platform_confirmed\n"
                       b"verification_status: verified\n---\n# Method\n\0")
    with pytest.raises(ValueError, match="contains binary data"):
        approve_draft(binary.name, inbox_dir=inbox, source_dir=source, index_root=root)
    assert binary.exists()


def test_approval_rejects_linked_destination_parent(tmp_path, monkeypatch):
    inbox, source, root = tmp_path / "inbox", tmp_path / "local", tmp_path / "index"
    (inbox / "nested").mkdir(parents=True)
    source.mkdir()
    draft = inbox / "nested" / "reviewed.md"
    draft.write_text("---\nsource_challenge: Demo\nconfirmation_source: platform_confirmed\n"
                     "verification_status: verified\n---\n# Method\n", encoding="utf-8")
    original = local_module._is_link
    monkeypatch.setattr(local_module, "_is_link",
                        lambda path: path == source / "nested" or original(path))
    with pytest.raises(ValueError, match="destination must not contain"):
        approve_draft("nested/reviewed.md", inbox_dir=inbox, source_dir=source, index_root=root)
    assert draft.exists()


def test_concurrent_index_and_approval_publish_latest_corpus(tmp_path, monkeypatch):
    inbox, source, root = tmp_path / "inbox", tmp_path / "local", tmp_path / "index"
    inbox.mkdir()
    source.mkdir()
    (source / "base.md").write_text("# Base\nPostgreSQL", encoding="utf-8")
    (inbox / "reviewed.md").write_text(
        "---\nsource_challenge: Demo\nconfirmation_source: platform_confirmed\n"
        "verification_status: verified\n---\n# Approved\napprovedterm\n", encoding="utf-8")
    index_started, release_index, approval_done = threading.Event(), threading.Event(), threading.Event()
    errors = []
    original = LocalKnowledge._index_locked.__func__

    def blocked_index(cls, source_dir, index_root):
        if threading.current_thread().name == "first-index":
            index_started.set()
            assert release_index.wait(10)
        return original(cls, source_dir, index_root)

    monkeypatch.setattr(LocalKnowledge, "_index_locked", classmethod(blocked_index))

    def index_worker():
        try:
            LocalKnowledge.index(source, root)
        except Exception as exc:
            errors.append(exc)

    def approve_worker():
        try:
            approve_draft("reviewed.md", inbox_dir=inbox, source_dir=source, index_root=root)
        except Exception as exc:
            errors.append(exc)
        finally:
            approval_done.set()

    first = threading.Thread(target=index_worker, name="first-index")
    second = threading.Thread(target=approve_worker, name="approval")
    first.start()
    try:
        assert index_started.wait(10)
        second.start()
        assert not approval_done.wait(0.15)
    finally:
        release_index.set()
        first.join(10)
        if second.ident is not None:
            second.join(10)
    assert not first.is_alive() and not second.is_alive()
    assert not errors
    assert LocalKnowledge(root).search("approvedterm")


def test_snippet_is_centered_on_match_in_long_chunk(tmp_path):
    source, root = tmp_path / "local", tmp_path / "index"
    source.mkdir()
    (source / "long.md").write_text("# Method\n" + "filler " * 240 +
                                     "distinctive_oracle_indicator at the end", encoding="utf-8")
    LocalKnowledge.index(source, root)
    snippet = LocalKnowledge(root).search("distinctive_oracle_indicator")[0]["snippet"]
    assert "distinctive_oracle_indicator" in snippet
    assert len(snippet) <= 800


def test_retrieval_expands_once_only_after_no_results(tmp_path):
    class SpyIndex:
        available = True
        snapshot_id = "spy"

        def __init__(self):
            self.calls = []

        def search(self, query, **kwargs):
            self.calls.append(kwargs["expand"])
            return []

    service = _service(tmp_path, tmp_path, tmp_path / "missing", "legacy")
    external, local = SpyIndex(), SpyIndex()
    service.external, service.local, service.enabled = external, local, True
    assert service.search("pgsql boolean oracle") == []
    assert external.calls == [False, True]
    assert local.calls == [False, True]

    class BrokenIndex(SpyIndex):
        def search(self, query, **kwargs):
            raise sqlite3.DatabaseError("corrupt index")

    service.external, service.local = BrokenIndex(), SpyIndex()
    failed = service.search("PostgreSQL oracle")
    assert failed == []
    assert failed.errors == ("spy:DatabaseError",)


@pytest.mark.asyncio
async def test_per_attempt_query_budget_reuses_queries():
    class FakeService:
        def __init__(self):
            self.calls = []

        async def search_async(self, query, **kwargs):
            self.calls.append(query)
            return [{"document_id": query}]

    service = FakeService()
    budget = KnowledgeQueryBudget(service, max_queries=2)
    assert await budget.search_async("PostgreSQL") == await budget.search_async("postgresql")
    assert await budget.search_async("boolean oracle")
    assert await budget.search_async("third unique query") == []
    assert len(service.calls) == 2
    budget.reset()
    assert await budget.search_async("third unique query")


def test_shared_prompt_and_three_adapters_read_local_result(tmp_path, monkeypatch):
    from backend.agents.codex_solver import CodexSolver

    source, root = tmp_path / "local", tmp_path / "index"
    source.mkdir()
    (source / "method.md").write_text("# PostgreSQL boolean oracle\npgsql evidence\n", encoding="utf-8")
    LocalKnowledge.index(source, root)
    pin_local_snapshot("adapter-run", root)
    service = _service(tmp_path, source, root, "adapter-run")
    prompt = build_prompt(ChallengeMeta(name="demo", category="web"), [])
    for phrase in ("search_knowledge", "read_knowledge", "database", "oracle", "synonym"):
        assert phrase in prompt

    deps = SimpleNamespace(knowledge_service=service, knowledge_query_budget=None)
    api = json.loads(asyncio.run(search_knowledge(SimpleNamespace(deps=deps), "pgsql evidence")))
    codex = CodexSolver.__new__(CodexSolver)
    codex.knowledge_service = service
    codex.knowledge_query_budget = None
    assert json.loads(asyncio.run(codex._exec_tool("search_knowledge", {"query": "pgsql evidence"}))) == api
    document_id = api[0]["document_id"]
    api_read = json.loads(asyncio.run(read_knowledge(SimpleNamespace(deps=deps), document_id)))
    assert json.loads(asyncio.run(codex._exec_tool("read_knowledge", {"document_id": document_id}))) == api_read

    captured = {}

    def capture_server(name, *, tools):
        captured.update({tool.name: tool for tool in tools})
        return {"type": "sdk", "name": name}

    monkeypatch.setattr("claude_agent_sdk.create_sdk_mcp_server", capture_server)
    make_claude_knowledge_server(service, None)
    claude_search = asyncio.run(captured["search_knowledge"].handler({"query": "pgsql evidence"}))
    claude_read = asyncio.run(captured["read_knowledge"].handler({"document_id": document_id}))
    assert json.loads(claude_search["content"][0]["text"]) == api
    assert json.loads(claude_read["content"][0]["text"]) == api_read


def test_upstream_navigation_keyword_still_maps_to_linked_document(tmp_path):
    root = tmp_path / "external"
    snapshot = root / "snapshots" / ("a" * 40 + "-v5")
    source = snapshot / "source"
    source.mkdir(parents=True)
    (source / "SQL.md").write_text("# SQL\nlinked content\n", encoding="utf-8")
    (source / "AI-SEARCH-INDEX.md").write_text(
        "### SQL注入\n- [SQL](SQL.md)\n- **关键词**: `特殊布尔术语`\n", encoding="utf-8")
    ExternalKnowledge._build(source, snapshot / "index.sqlite3", ExternalKnowledge(root, "disabled"))
    external = ExternalKnowledge(root, snapshot.name)
    assert any(hit["path"] == "SQL.md" for hit in external.search("特殊布尔术语"))
