from __future__ import annotations

import asyncio
import hashlib
import json
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.solver_mcp import (
    BROKER_TOOL_SPECS,
    AnalysisFile,
    ChallengeAnalysis,
    McpConnection,
    SolverMcpGateway,
    make_claude_analysis_server,
)


def _gateway(tmp_path: Path, **settings) -> SolverMcpGateway:
    path = tmp_path / "solver-mcp.json"
    path.write_text(json.dumps({"runtime_dir": str(tmp_path / "runtime"), **settings}), encoding="utf-8")
    return SolverMcpGateway(path)


@pytest.mark.asyncio
async def test_safe_nested_archive_discovery_and_apk_classification(tmp_path: Path) -> None:
    challenge = tmp_path / "challenge"
    distfiles = challenge / "distfiles"
    distfiles.mkdir(parents=True)
    binary = distfiles / "solver"
    binary.write_bytes(b"\x7fELF\x02\x01" + b"\0" * 64)

    apk_bytes_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_bytes_path, "w") as apk:
        apk.writestr("AndroidManifest.xml", '<manifest package="org.example.test"/>')
        apk.writestr("classes.dex", b"dex\n035\0")
    nested_apk = apk_bytes_path.read_bytes()

    outer = distfiles / "bundle.zip"
    with zipfile.ZipFile(outer, "w") as bundle:
        bundle.writestr("nested/sample.apk", nested_apk)
        bundle.writestr("../escaped.txt", b"must not escape")

    gateway = _gateway(tmp_path)
    analysis_dir = gateway.runtime_root / "challenge"
    analysis_dir.mkdir(parents=True)
    analysis = ChallengeAnalysis("test", challenge, analysis_dir)
    files = gateway._collect_analysis_files(analysis)

    assert {item.kind for item in files} == {"binary", "apk"}
    apk_path = next(item.path for item in files if item.kind == "apk")
    assert SolverMcpGateway._apk_package(apk_path) == "org.example.test"
    assert SolverMcpGateway._manifest_matches(
        {"content": '<manifest package="org.example.test"/>'}, apk_path
    )
    assert not SolverMcpGateway._manifest_matches(
        {"content": '<manifest package="org.example.other"/>'}, apk_path
    )
    assert not (analysis_dir / "files" / "escaped.txt").exists()
    assert all(item.path.is_relative_to(analysis_dir) for item in files)


class _McpResult:
    def __init__(self, payload: dict) -> None:
        self.is_error = False
        self.structured_content = payload
        self.content = []


@pytest.mark.asyncio
async def test_ida_calls_are_bound_to_challenge_session_and_file_hash(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    gateway.connections["ida"] = McpConnection(
        "ida", {}, tools={"decompile": {"name": "decompile"}}, state="ready"
    )
    captured: list[dict] = []

    async def call_raw(server: str, tool_name: str, arguments: dict):
        captured.append(dict(arguments))
        return _McpResult({"used": arguments.get("database")})

    gateway._call_raw = call_raw  # type: ignore[method-assign]
    analyses: dict[str, ChallengeAnalysis] = {}
    for challenge, session in (("challenge-a", "session-a"), ("challenge-b", "session-b")):
        root = tmp_path / challenge
        root.mkdir()
        binary = root / "target"
        binary.write_bytes(b"\x7fELF" + challenge.encode())
        digest = hashlib.sha256(binary.read_bytes()).hexdigest()
        file_id = f"{digest[:12]}:target"
        item = AnalysisFile(file_id, "target", binary, digest, "binary", "ready", session)
        item.ida_ready_event.set()
        analysis = ChallengeAnalysis(challenge, root, root / "analysis", files={file_id: item})
        analyses[challenge] = analysis
        gateway._challenges[challenge] = analysis

    for challenge, session in (("challenge-a", "session-a"), ("challenge-b", "session-b")):
        file_id = next(iter(analyses[challenge].files))
        result = await gateway.call_analysis_tool(
            challenge, "ida", "decompile", {"database": "attacker-selected-session"}, file_id
        )
        assert result["ok"] is True
        assert result["result"]["used"] == session

    rejected = await gateway.call_analysis_tool("challenge-a", "ida", "decompile", {}, "challenge-b-file-id")
    assert rejected["ok"] is False
    assert "Unknown or incompatible" in rejected["error"]
    assert [args["database"] for args in captured] == ["session-a", "session-b"]


@pytest.mark.asyncio
async def test_ida_session_reopens_after_mcp_connection_changes(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    connection = McpConnection(
        "ida", {}, tools={"decompile": {"name": "decompile"}, "idb_open": {"name": "idb_open"}},
        state="ready", generation=2,
    )
    connection.session = object()  # type: ignore[assignment]
    gateway.connections["ida"] = connection
    binary = tmp_path / "target.so"
    binary.write_bytes(b"\x7fELF session recovery")
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    item = AnalysisFile(f"{digest[:16]}:target.so", "target.so", binary, digest, "binary", "ready", "old-session", 1)
    item.ida_ready_event.set()
    gateway._challenges["challenge"] = ChallengeAnalysis(
        "challenge", tmp_path, tmp_path / "analysis", files={item.file_id: item}
    )

    async def call_raw(server: str, tool_name: str, arguments: dict):
        if tool_name == "idb_open":
            return _McpResult({"success": True, "session": {"session_id": "new-session"}})
        return _McpResult({"database": arguments["database"]})

    gateway._call_raw = call_raw  # type: ignore[method-assign]
    result = await gateway.call_analysis_tool("challenge", "ida", "decompile", {}, item.file_id)
    assert result["ok"] is True
    assert result["result"]["database"] == "new-session"
    assert item.ida_generation == connection.generation


@pytest.mark.asyncio
async def test_tool_input_error_does_not_reconnect_ida(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    connection = McpConnection("ida", {}, tools={"decompile": {"name": "decompile"}}, state="ready")
    gateway.connections["ida"] = connection
    binary = tmp_path / "target.so"
    binary.write_bytes(b"\x7fELF bad input")
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    item = AnalysisFile(f"{digest[:16]}:target.so", "target.so", binary, digest, "binary", "ready", "session")
    item.ida_ready_event.set()
    gateway._challenges["challenge"] = ChallengeAnalysis(
        "challenge", tmp_path, tmp_path / "analysis", files={item.file_id: item}
    )

    async def call_raw(server: str, tool_name: str, arguments: dict):
        return _McpResult({"error": "Invalid params: missing queries"})

    async def no_disconnect(connection: McpConnection) -> None:
        raise AssertionError("A tool input error must not restart the MCP server")

    gateway._call_raw = call_raw  # type: ignore[method-assign]
    gateway._disconnect = no_disconnect  # type: ignore[method-assign]
    result = await gateway.call_analysis_tool("challenge", "ida", "decompile", {}, item.file_id)
    assert result["ok"] is False
    assert "Invalid params" in result["error"]


@pytest.mark.asyncio
async def test_jadx_gui_lease_serializes_challenges(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    await gateway._acquire_jadx_lease("challenge-a")
    waiting = asyncio.create_task(gateway._acquire_jadx_lease("challenge-b"))
    await asyncio.sleep(0)
    assert not waiting.done()

    await gateway.release_challenge("challenge-a")
    await waiting
    assert gateway._jadx_owner == "challenge-b"
    await gateway.release_challenge("challenge-b")


@pytest.mark.asyncio
async def test_finished_swarm_releases_queued_jadx_preparation(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    await gateway._acquire_jadx_lease("challenge-a")
    queued = asyncio.create_task(gateway._acquire_jadx_lease("challenge-b"))
    gateway._challenges["challenge-b"] = ChallengeAnalysis(
        "challenge-b", tmp_path, tmp_path / "analysis", preparation_task=queued
    )
    await asyncio.sleep(0)
    await asyncio.wait_for(gateway.release_challenge("challenge-b"), timeout=1)
    assert queued.cancelled()
    assert gateway._jadx_owner == "challenge-a"
    await gateway.release_challenge("challenge-a")


@pytest.mark.asyncio
async def test_queued_jadx_call_does_not_hold_gui_lock(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    gateway.connections["jadx"] = McpConnection(
        "jadx", {}, tools={"get_android_manifest": {"name": "get_android_manifest"}}, state="ready"
    )
    apk = tmp_path / "test.apk"
    apk.write_bytes(b"test bytes")
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    item = AnalysisFile(f"{digest[:16]}:test.apk", "test.apk", apk, digest, "apk", jadx_state="queued")
    gateway._challenges["challenge-b"] = ChallengeAnalysis(
        "challenge-b", tmp_path, tmp_path / "analysis", files={item.file_id: item}
    )
    gateway._jadx_active_file = str(apk.resolve())
    gateway._jadx_process = SimpleNamespace(returncode=None)  # type: ignore[assignment]
    await gateway._acquire_jadx_lease("challenge-a")

    async def call_raw(server: str, tool_name: str, arguments: dict):
        return _McpResult({"content": "ready"})

    gateway._call_raw = call_raw  # type: ignore[method-assign]
    pending = asyncio.create_task(
        gateway.call_analysis_tool(
            "challenge-b", "jadx", "get_android_manifest", {}, item.file_id
        )
    )
    await asyncio.sleep(0)
    assert not gateway._jadx_lock.locked()
    assert not pending.done()

    item.jadx_state = "ready"
    item.jadx_ready_event.set()
    await gateway.release_challenge("challenge-a")
    result = await asyncio.wait_for(pending, timeout=1)
    assert result["ok"] is True
    await gateway.release_challenge("challenge-b")


@pytest.mark.asyncio
async def test_jadx_readiness_has_a_wall_clock_deadline(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path, jadx_ready_timeout_seconds=0.05)
    apk = tmp_path / "test.apk"
    apk.write_bytes(b"not needed for timeout")
    item = AnalysisFile("test", "test.apk", apk, "", "apk")
    analysis = ChallengeAnalysis("challenge", tmp_path, tmp_path / "analysis")

    async def slow_manifest(server: str, tool_name: str, arguments: dict):
        await asyncio.sleep(60)

    gateway._call_raw = slow_manifest  # type: ignore[method-assign]
    assert await asyncio.wait_for(gateway._wait_jadx_loaded(analysis, item), timeout=1) is False


@pytest.mark.asyncio
async def test_kali_tools_are_listed_for_challenge_without_files(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    gateway.connections["kali"] = McpConnection(
        "kali", {}, tools={"server_health": {"name": "server_health"}}, state="ready"
    )
    analysis = ChallengeAnalysis("ctf", tmp_path, tmp_path / "analysis", state="starting")
    gateway._challenges["ctf"] = analysis

    assert gateway.analysis_status("ctf")["challenges"][0]["state"] == "starting"
    listed = await gateway.list_analysis_tools("ctf")
    assert [tool["name"] for tool in listed["tools"]] == ["server_health"]


def test_mcp_tool_schema_uses_sdk_v2_field_names() -> None:
    assert SolverMcpGateway._tool_input_schema(
        SimpleNamespace(input_schema={"type": "object"})
    ) == {"type": "object"}

    class DeprecatedTool:
        input_schema = None

        def __getattr__(self, name: str):
            if name == "inputSchema":
                raise AssertionError("deprecated MCP schema alias was accessed")
            raise AttributeError(name)

    assert SolverMcpGateway._tool_input_schema(DeprecatedTool()) == {}


def test_mcp_result_helpers_prefer_v2_snake_case_fields() -> None:
    class V2Result:
        structured_content = {"ok": True}
        is_error = False

        def __getattr__(self, name: str):
            if name in {"structuredContent", "isError"}:
                raise AssertionError(f"deprecated MCP field {name} was accessed")
            raise AttributeError(name)

    result = V2Result()
    assert SolverMcpGateway._result_data(result) == {"ok": True}
    assert SolverMcpGateway._result_is_error(result) is False

    class V2ResultWithoutStructuredContent:
        structured_content = None
        is_error = False
        content = [SimpleNamespace(type="text", text='{"ok": true}')]

        def __getattr__(self, name: str):
            if name in {"structuredContent", "isError"}:
                raise AssertionError(f"deprecated MCP field {name} was accessed")
            raise AttributeError(name)

    empty = V2ResultWithoutStructuredContent()
    assert SolverMcpGateway._result_data(empty) == {"ok": True}
    assert SolverMcpGateway._result_is_error(empty) is False


def test_mcp_textual_errors_are_detected() -> None:
    assert SolverMcpGateway._result_is_error(_McpResult({"error": "bad input"}))
    result = SimpleNamespace(isError=False, structuredContent=None, content=[SimpleNamespace(type="text", text="Invalid params: missing value")])
    assert SolverMcpGateway._result_is_error(result)


@pytest.mark.asyncio
async def test_kali_disconnect_is_reported_without_aborting_solver_flow(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    gateway.connections["kali"] = McpConnection(
        "kali", {}, state="unavailable", error="connection refused"
    )

    result = await gateway.call_analysis_tool(
        "challenge", "kali", "server_health", {}
    )
    assert result["ok"] is False
    assert "unavailable" in result["error"]


@pytest.mark.asyncio
async def test_stdio_context_is_closed_by_the_task_that_opened_it(tmp_path: Path, monkeypatch) -> None:
    import backend.solver_mcp as solver_mcp

    task_ids: dict[str, int] = {}

    @asynccontextmanager
    async def fake_stdio_client(_params):
        task_ids["stdio_enter"] = id(asyncio.current_task())
        try:
            yield object(), object()
        finally:
            task_ids["stdio_exit"] = id(asyncio.current_task())

    class FakeSession:
        async def __aenter__(self):
            task_ids["session_enter"] = id(asyncio.current_task())
            return self

        async def __aexit__(self, *_exc):
            task_ids["session_exit"] = id(asyncio.current_task())

        async def initialize(self):
            return None

        async def list_tools(self):
            return SimpleNamespace(tools=[])

    monkeypatch.setattr(solver_mcp, "stdio_client", fake_stdio_client)
    monkeypatch.setattr(solver_mcp, "ClientSession", lambda *_args: FakeSession())
    gateway = _gateway(tmp_path)
    gateway.connections["ida"] = McpConnection("ida", {"command": "fake-mcp"})

    await gateway.start()
    owner = gateway.connections["ida"].owner_task
    assert owner is not None and owner is not asyncio.current_task()
    await gateway.close()

    assert task_ids["stdio_enter"] == task_ids["stdio_exit"]
    assert task_ids["session_enter"] == task_ids["session_exit"]


@pytest.mark.asyncio
async def test_ida_session_management_tools_are_gateway_only(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    gateway.connections["ida"] = McpConnection(
        "ida",
        {},
        tools={
            "idb_open": {"name": "idb_open"},
            "idb_list": {"name": "idb_list"},
            "decompile": {
                "name": "decompile",
                "input_schema": {
                    "type": "object",
                    "properties": {"database": {"type": "string"}, "addr": {"type": "string"}},
                    "required": ["database", "addr"],
                },
            },
        },
        state="ready",
    )
    path = tmp_path / "target"
    path.write_bytes(b"\x7fELF sample")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    item = AnalysisFile(f"{digest[:16]}:target", "target", path, digest, "binary", "ready", "session")
    item.ida_ready_event.set()
    gateway._challenges["challenge"] = ChallengeAnalysis(
        "challenge", tmp_path, tmp_path / "analysis", files={item.file_id: item}
    )

    tools = await gateway.list_analysis_tools("challenge")
    assert [tool["name"] for tool in tools["tools"]] == ["decompile"]
    assert "database" not in tools["tools"][0]["input_schema"]["properties"]
    assert tools["tools"][0]["input_schema"]["required"] == ["addr"]
    assert "session" not in gateway.analysis_status("challenge")["challenges"][0]["files"][0]["ida"]
    blocked = await gateway.call_analysis_tool("challenge", "ida", "idb_open", {})
    assert blocked["ok"] is False


def test_corrupt_archive_is_ignored_and_size_limits_are_enforced(tmp_path: Path) -> None:
    challenge = tmp_path / "challenge"
    distfiles = challenge / "distfiles"
    distfiles.mkdir(parents=True)
    broken = distfiles / "broken.zip"
    broken.write_bytes(b"not a zip")
    gateway = _gateway(tmp_path, max_extracted_bytes=16)
    analysis_dir = gateway.runtime_root / "challenge"
    analysis_dir.mkdir(parents=True)
    analysis = ChallengeAnalysis("broken", challenge, analysis_dir)
    assert gateway._collect_analysis_files(analysis) == []
    assert broken.exists()

    (distfiles / "large.bin").write_bytes(b"\x7fELF" + b"x" * 32)
    with pytest.raises(ValueError, match="size limit"):
        gateway._collect_analysis_files(analysis)


@pytest.mark.asyncio
async def test_all_solver_backends_receive_the_same_broker_tools() -> None:
    from backend.agents.codex_solver import CodexSolver
    from backend.agents.solver import _build_toolset

    api_tools = _build_toolset(SimpleNamespace(use_vision=False, analysis_gateway=object()))
    expected = {"list_analysis_tools", "call_analysis_tool", "analysis_status"}
    assert expected.issubset(api_tools.tools)
    assert expected.issubset({tool["name"] for tool in BROKER_TOOL_SPECS})
    assert make_claude_analysis_server(object(), "challenge")["type"] == "sdk"

    class FakeGateway:
        async def call_analysis_tool(self, challenge, server, tool_name, arguments, file_id):
            return {"challenge": challenge, "server": server, "tool": tool_name, "file_id": file_id}

    solver = CodexSolver.__new__(CodexSolver)
    solver.analysis_gateway = FakeGateway()
    solver.meta = SimpleNamespace(name="challenge")
    result = json.loads(
        await solver._exec_tool(
            "call_analysis_tool",
            {"server": "ida", "tool_name": "decompile", "file_id": "bound-file"},
        )
    )
    assert result["challenge"] == "challenge"
    assert result["file_id"] == "bound-file"
