import asyncio
import json
import logging
from types import SimpleNamespace

import pytest

from backend.external_knowledge import ExternalKnowledge, pin_snapshot
from backend.knowledge import KnowledgeQuery, KnowledgeRecord, KnowledgeStore
from backend.knowledge_service import KnowledgeService


@pytest.fixture
def fixture_index(tmp_path):
    root = tmp_path / "knowledge"
    snapshot = root / "snapshots" / ("a" * 40 + "-v5")
    source = snapshot / "source"
    source.mkdir(parents=True)
    (source / "SQL.md").write_text("# SQL注入\n\n## 宽字节注入\nGBK 宽字节 绕过 技巧\n\n```sql\nSELECT * FROM users;\n```\n", encoding="utf-8")
    (source / "AI-SEARCH-INDEX.md").write_text("### SQL技巧\n- [知识](SQL.md)\n- **关键词**: `特殊术语`\n", encoding="utf-8")
    script_dir = source / "CTF常用脚本及工具" / "图片爆破宽高"
    script_dir.mkdir(parents=True)
    (script_dir / "修复.py").write_text("# IHDR CRC 图片宽高\nprint('ok')\n", encoding="utf-8")
    (script_dir / "运行").write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
    (script_dir / "data.bin").write_bytes(b"\x00\xff\x10")
    ExternalKnowledge._build(source, snapshot / "index.sqlite3", ExternalKnowledge(root, "missing"))
    (root / "current.json").write_text(json.dumps({"snapshot_id": snapshot.name}), encoding="utf-8")
    return ExternalKnowledge(root)


def test_search_read_and_pin(fixture_index):
    source = fixture_index
    hits = source.search("GBK 宽字节")
    assert hits and hits[0]["path"] == "SQL.md"
    assert any(item["path"] == "SQL.md" for item in source.search("特殊术语"))
    doc = source.read(hits[0]["document_id"], start_line=1, line_count=2)
    assert "SQL注入" in doc["text"]
    assert doc["next_start_line"] == 3
    assert source.search("不存在的术语", category="web") == []
    first = pin_snapshot(source.root, "run1")
    (source.root / "current.json").write_text(json.dumps({"snapshot_id": "new-version"}), encoding="utf-8")
    assert pin_snapshot(source.root, "run1") == first


def test_long_noisy_queries_retrieve_late_clues(fixture_index):
    source = fixture_index
    noisy = "GBK 宽字节 " + " ".join(f"zznoise{index:02d}" for index in range(16))
    assert any(item["path"] == "SQL.md" for item in source.search(noisy))
    late = " ".join(f"zznoise{index:02d}" for index in range(64)) + " IHDR CRC"
    assert any(item["path"].endswith("修复.py") for item in source.search(late, kind="script"))
    assert source.search("完全不存在的随机术语 qxjvzp") == []


def test_copy_program_variant_aliases_recall_role_document(tmp_path):
    root = tmp_path / "knowledge"
    snapshot = root / "snapshots" / ("b" * 40 + "-v5")
    source = snapshot / "source"
    source.mkdir(parents=True)
    (source / "role.md").write_text(
        "# Database role check\npg_execute_server_program membership grants server execution.\n",
        encoding="utf-8",
    )
    ExternalKnowledge._build(source, snapshot / "index.sqlite3", ExternalKnowledge(root, "missing"))
    index = ExternalKnowledge(root, snapshot.name)
    for query in ("COPY FROM/TO PROGRAM", "COPY ... TO PROGRAM", "COPY…TO PROGRAM"):
        assert index.search(query, expand=False) == []
        assert any(hit["path"] == "role.md" for hit in index.search(query, expand=True))


def test_snippet_prefers_original_query_over_early_alias(tmp_path):
    root = tmp_path / "knowledge"
    snapshot = root / "snapshots" / ("c" * 40 + "-v5")
    source = snapshot / "source"
    source.mkdir(parents=True)
    (source / "method.md").write_text(
        "# Database method\n数据库 " + "filler " * 180 + "PostgreSQL permission oracle\n",
        encoding="utf-8",
    )
    ExternalKnowledge._build(source, snapshot / "index.sqlite3", ExternalKnowledge(root, "missing"))
    index = ExternalKnowledge(root, snapshot.name)
    hit = index.search("PostgreSQL", expand=True)[0]
    assert "PostgreSQL" in hit["snippet"]
    assert len(hit["snippet"]) <= 800


def test_kind_filter_applies_before_fts_candidate_limit(tmp_path):
    root = tmp_path / "knowledge"
    snapshot = root / "snapshots" / ("d" * 40 + "-v5")
    source = snapshot / "source"
    writeups = source / "WP汇总"
    writeups.mkdir(parents=True)
    for number in range(60):
        (writeups / f"{number:03}.md").write_text(
            f"# Target\nTarget matching content {number}\n", encoding="utf-8"
        )
    (source / "zzarticle.md").write_text("# Other\nTarget content\n", encoding="utf-8")
    ExternalKnowledge._build(source, snapshot / "index.sqlite3", ExternalKnowledge(root, "missing"))
    index = ExternalKnowledge(root, snapshot.name)
    assert index.search("Target", kind="article")[0]["path"] == "zzarticle.md"


def test_sync_reuses_existing_commit_without_cloning(fixture_index, monkeypatch):
    calls = []

    def fake_git(args, *, cwd=None):
        calls.append(args)
        return "a" * 40 + "\trefs/heads/main"

    monkeypatch.setattr(ExternalKnowledge, "_git", fake_git)
    manifest = ExternalKnowledge.sync(fixture_index.root)
    assert manifest["snapshot_id"] == fixture_index.snapshot_id
    assert len(calls) == 1
    assert calls[0][0] == "ls-remote"


class FakeSandbox:
    def __init__(self):
        self.files = {}

    async def exec(self, command, timeout_s=10):
        if command.startswith("test -e"):
            return SimpleNamespace(exit_code=0 if any(path in command for path in self.files) else 1)
        return SimpleNamespace(exit_code=0)

    async def read_file_bytes(self, path):
        return self.files[path]

    async def write_file(self, path, content):
        self.files[path] = content


def test_stage_script_and_conflict(fixture_index):
    source = fixture_index
    script = source.search("IHDR CRC", kind="script")[0]
    read = source.read(script["document_id"])
    dependency = next(item for item in read["related_files"] if item["path"].endswith("data.bin"))
    no_extension = next(item for item in read["related_files"] if item["path"].endswith("运行"))
    assert no_extension["kind"] == "script"
    sandbox = FakeSandbox()
    result = asyncio.run(source.stage(sandbox, script["document_id"], [dependency["document_id"]]))
    assert len(result["files"]) == 2
    assert all(path.startswith("/challenge/workspace/knowledge/") for path in sandbox.files)
    assert all(path.count("\\") == 0 for path in sandbox.files)
    reused = asyncio.run(source.stage(sandbox, script["document_id"], [dependency["document_id"]]))
    assert all(item["reused"] for item in reused["files"])
    sandbox.files[result["files"][0]["path"]] = b"modified"
    conflict = asyncio.run(source.stage(sandbox, script["document_id"]))
    assert conflict["conflicts"]
    assert sandbox.files[result["files"][0]["path"]] == b"modified"


def test_readonly_index_connections_close_after_each_operation(fixture_index, monkeypatch):
    import backend.external_knowledge as knowledge_module

    original_connect = knowledge_module._connect_readonly
    connections = []

    class TrackedConnection:
        def __init__(self, inner):
            self.inner = inner
            self.closed = False

        def __enter__(self):
            self.inner.__enter__()
            return self

        def __exit__(self, *args):
            return self.inner.__exit__(*args)

        def __getattr__(self, name):
            return getattr(self.inner, name)

        def close(self):
            self.closed = True
            self.inner.close()

    def connect(path):
        connection = TrackedConnection(original_connect(path))
        connections.append(connection)
        return connection

    monkeypatch.setattr(knowledge_module, "_connect_readonly", connect)
    source = fixture_index
    assert source.status()["documents"] > 0
    hit = source.search("GBK 宽字节")[0]
    assert source.read(hit["document_id"])["text"]
    script = source.search("IHDR CRC", kind="script")[0]
    asyncio.run(source.stage(FakeSandbox(), script["document_id"]))
    assert len(connections) == 5
    assert all(connection.closed for connection in connections)


def test_unified_service_and_context(fixture_index, tmp_path):
    settings = SimpleNamespace(external_knowledge_enabled=True, external_knowledge_dir=str(fixture_index.root),
                               challenge_run_id="run-service", external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3"))
    results = service.search("GBK 宽字节", category="web")
    assert results and results[0]["source"] == "Des-CTF-Knowledge"
    assert "knowledge_reference_untrusted" in service.initial_context(
        KnowledgeQuery(name="SQL注入", category="web", description="GBK 宽字节"))
    assert service.initial_context(KnowledgeQuery(name="", category="web")) == ""


def test_initial_context_uses_late_description_and_respects_budget(fixture_index, tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="backend.knowledge_service")
    settings = SimpleNamespace(external_knowledge_enabled=True, external_knowledge_dir=str(fixture_index.root),
                               challenge_run_id="long-context", external_knowledge_context_items=4,
                               external_knowledge_context_chars=1000)
    service = KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3"))
    description = " ".join(f"zznoise{index:02d}" for index in range(64)) + " GBK 宽字节"
    context = service.initial_context(KnowledgeQuery(name="unrelated-title", category="web", description=description))
    assert "SQL.md" in context
    assert len(context) <= 1000
    assert context.count("[Des-CTF-Knowledge;") <= 4
    assert "query_groups=2" in caplog.text


def test_initial_context_uses_distinct_external_documents(fixture_index, tmp_path, monkeypatch):
    settings = SimpleNamespace(external_knowledge_enabled=True, external_knowledge_dir=str(fixture_index.root),
                               challenge_run_id="distinct-context", external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3"))
    base = fixture_index.search("GBK 宽字节")[0]
    hits = [dict(base, document_id="doc0", path="doc0.md"),
            dict(base, document_id="doc0", path="doc0.md", start_line=99)]
    hits.extend(dict(base, document_id=f"doc{index}", path=f"doc{index}.md") for index in range(1, 5))
    monkeypatch.setattr(service.external, "search", lambda query, *, category, limit: hits)
    context = service.initial_context(KnowledgeQuery(name="GBK", description="宽字节"))
    assert context.count("doc0 doc0.md") == 1
    assert context.count("[Des-CTF-Knowledge;") == 4


def test_verified_memory_is_ranked_from_full_query_and_can_be_read(tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="backend.knowledge_service")
    store = KnowledgeStore(tmp_path / "memory.sqlite3")
    records = [
        KnowledgeRecord("other", "web", "attachment", "shared technique", "shared evidence", "accepted", "model"),
        KnowledgeRecord("target", "web", "remote", "shared technique",
                        "shared evidence with flag: secret " + "x" * 5000, "accepted", "model"),
        KnowledgeRecord("target", "web", "remote", "unverified technique", "shared evidence candidate", "unverified_candidate", "model"),
    ]
    for record in records:
        assert store.remember(record)
    settings = SimpleNamespace(external_knowledge_enabled=False, external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, store)
    query = KnowledgeQuery(name="target", category="web", mode="remote", description="shared evidence")
    context = service.initial_context(query)
    expected = "memory:" + store._digest(records[1])
    assert expected in context
    assert "unverified_candidate" not in context
    assert "unverified technique" not in context
    assert '"source": "local-memory"' in caplog.text
    assert '"outcome": "accepted"' in caplog.text
    assert "shared evidence" not in caplog.text
    explicit = service.search("shared evidence", kind="memory", limit=10)
    assert any(item["outcome"] == "unverified_candidate" for item in explicit)
    assert all(len(item["document_id"].removeprefix("memory:")) == 64 for item in explicit)
    result = asyncio.run(service.read_async(expected))
    assert result["document_id"] == expected
    assert result["outcome"] == "accepted"
    assert "shared evidence" in result["text"]
    assert "secret" not in result["text"]
    assert len(result["text"]) <= 4003
    assert result["next_start_line"] is None
    assert result["next_char_offset"] == 0
    with pytest.raises(ValueError, match="Invalid memory document ID"):
        asyncio.run(service.read_async("memory:bad"))
    with pytest.raises(ValueError, match="Unknown memory document ID"):
        asyncio.run(service.read_async("memory:" + "0" * 64))
    with pytest.raises(ValueError, match="cannot be staged"):
        asyncio.run(service.stage_async(FakeSandbox(), expected))


def test_three_solver_tool_adapters_share_results(fixture_index, tmp_path, monkeypatch):
    from backend.agents.codex_solver import CodexSolver
    from backend.agents.solver import _build_toolset
    from backend.knowledge_service import make_claude_knowledge_server
    from backend.tools.knowledge import KNOWLEDGE_TOOL_SPECS, read_knowledge, search_knowledge

    settings = SimpleNamespace(external_knowledge_enabled=True, external_knowledge_dir=str(fixture_index.root),
                               challenge_run_id="adapter-test", external_knowledge_context_items=4,
                               external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, KnowledgeStore(tmp_path / "memory.sqlite3"))
    fake_sandbox = FakeSandbox()
    deps = SimpleNamespace(use_vision=False, analysis_gateway=None, knowledge_service=service,
                           sandbox=fake_sandbox)
    api_tools = _build_toolset(deps)
    expected = {"search_knowledge", "read_knowledge", "stage_knowledge_script"}
    assert expected.issubset(api_tools.tools)
    assert expected == {tool["name"] for tool in KNOWLEDGE_TOOL_SPECS}
    assert make_claude_knowledge_server(service, fake_sandbox)["type"] == "sdk"

    codex = CodexSolver.__new__(CodexSolver)
    codex.knowledge_service = service
    codex.sandbox = fake_sandbox
    api = json.loads(asyncio.run(search_knowledge(SimpleNamespace(deps=deps), "GBK 宽字节")))
    codex_results = json.loads(asyncio.run(codex._exec_tool("search_knowledge", {"query": "GBK 宽字节"})))
    assert codex_results == api
    record = KnowledgeRecord("demo", "web", "attachment", "GBK method", "GBK evidence with details", "accepted", "model")
    assert service.memory.remember(record)
    memory_id = service.search("GBK evidence", kind="memory")[0]["document_id"]
    api_read = json.loads(asyncio.run(read_knowledge(SimpleNamespace(deps=deps), memory_id)))
    codex_read = json.loads(asyncio.run(codex._exec_tool("read_knowledge", {"document_id": memory_id})))
    assert codex_read == api_read
    captured = {}

    def capture_server(name, *, tools):
        captured.update({tool.name: tool for tool in tools})
        return {"type": "sdk", "name": name}

    monkeypatch.setattr("claude_agent_sdk.create_sdk_mcp_server", capture_server)
    make_claude_knowledge_server(service, fake_sandbox)
    claude_read = asyncio.run(captured["read_knowledge"].handler({"document_id": memory_id}))
    assert json.loads(claude_read["content"][0]["text"]) == api_read
