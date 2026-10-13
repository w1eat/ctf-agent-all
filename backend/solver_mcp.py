"""Shared MCP gateway and automatic reverse-engineering preparation for solvers."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
import stat
import struct
import tarfile
import zipfile
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from mcp.client.stdio import StdioServerParameters, stdio_client

from mcp import ClientSession

logger = logging.getLogger(__name__)

MAX_ARCHIVE_DEPTH = 2
MAX_EXTRACTED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 10_000
MAX_TOOL_RESULT_CHARS = 50_000

BROKER_TOOL_SPECS = [
    {
        "name": "list_analysis_tools",
        "description": "List ready IDA, JADX, and Kali MCP tools for this challenge, with eligible analysis file IDs.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "analysis_status",
        "description": "Show MCP server connections and per-file IDA/JADX readiness for this challenge.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "call_analysis_tool",
        "description": "Call a discovered IDA, JADX, or Kali MCP tool. For IDA/JADX pass the file_id from list_analysis_tools. Put the target MCP tool arguments in arguments.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server": {"type": "string", "enum": ["ida", "jadx", "kali"]},
                "tool_name": {"type": "string"},
                "arguments": {"type": "object", "additionalProperties": True},
                "file_id": {"type": "string"},
            },
            "required": ["server", "tool_name"],
            "additionalProperties": False,
        },
    },
]


@dataclass
class McpConnection:
    name: str
    spec: dict[str, Any]
    session: ClientSession | None = None
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)
    state: str = "stopped"
    error: str = ""
    generation: int = 0
    owner_task: asyncio.Task[None] | None = None
    stop_event: asyncio.Event | None = None
    ready_future: asyncio.Future[bool] | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    call_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


@dataclass
class AnalysisFile:
    file_id: str
    relative_path: str
    path: Path
    sha256: str
    kind: str
    ida_state: str = "unavailable"
    ida_session: str = ""
    ida_generation: int = 0
    jadx_state: str = "unavailable"
    error: str = ""
    ida_ready_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
    jadx_ready_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)


@dataclass
class ChallengeAnalysis:
    challenge: str
    challenge_dir: Path
    work_dir: Path
    source_fingerprint: str = ""
    files: dict[str, AnalysisFile] = field(default_factory=dict)
    state: str = "queued"
    error: str = ""
    preparation_task: asyncio.Task[None] | None = None
    jadx_lease: bool = False


class SolverMcpGateway:
    """Own MCP subprocesses and bind analysis tool calls to one challenge."""

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path).expanduser().resolve()
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("Solver MCP config must be a JSON object")
        self.config = config
        servers = config.get("servers", config)
        if not isinstance(servers, dict):
            raise ValueError("Solver MCP config must contain a 'servers' object")
        self.connections: dict[str, McpConnection] = {}
        for name in ("ida", "jadx", "kali"):
            spec = servers.get(name)
            if isinstance(spec, dict) and spec.get("command"):
                self.connections[name] = McpConnection(name, spec)

        self.jadx_gui_spec = config.get("jadx_gui", {})
        self.runtime_root = Path(config.get("runtime_dir", ".runtime/solver-mcp")).expanduser()
        if not self.runtime_root.is_absolute():
            self.runtime_root = (Path.cwd() / self.runtime_root).resolve()
        self.max_archive_depth = int(config.get("max_archive_depth", MAX_ARCHIVE_DEPTH))
        self.max_extracted_bytes = int(config.get("max_extracted_bytes", MAX_EXTRACTED_BYTES))
        self.max_archive_entries = int(config.get("max_archive_entries", MAX_ARCHIVE_ENTRIES))
        self.connect_timeout = float(config.get("connect_timeout_seconds", 90))
        self.tool_timeout = float(config.get("tool_timeout_seconds", 300))
        self.jadx_ready_timeout = float(config.get("jadx_ready_timeout_seconds", 180))
        self._ida_preparation_limit = asyncio.Semaphore(max(1, int(config.get("ida_concurrency", 4))))
        self._challenges: dict[str, ChallengeAnalysis] = {}
        self._prep_lock = asyncio.Lock()
        self._jadx_lock = asyncio.Lock()
        self._jadx_condition = asyncio.Condition()
        self._jadx_owner: str | None = None
        self._jadx_active_file: str = ""
        self._jadx_process: asyncio.subprocess.Process | None = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self._started = True
        await asyncio.gather(
            *(self._connect(name) for name in ("ida", "kali") if name in self.connections),
            return_exceptions=True,
        )

    async def close(self) -> None:
        for analysis in self._challenges.values():
            task = analysis.preparation_task
            if task and not task.done():
                task.cancel()
        tasks = [a.preparation_task for a in self._challenges.values() if a.preparation_task]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await self._stop_jadx_gui()
        for connection in self.connections.values():
            await self._disconnect(connection)
        self._started = False

    async def _connect(self, name: str) -> bool:
        connection = self.connections.get(name)
        if not connection:
            return False
        async with connection.lock:
            if connection.session and connection.state == "ready":
                return True
            task = connection.owner_task
            ready = connection.ready_future
            if task is None or task.done() or ready is None:
                connection.state = "starting"
                connection.stop_event = asyncio.Event()
                connection.ready_future = asyncio.get_running_loop().create_future()
                task = asyncio.create_task(
                    self._connection_owner(connection, connection.stop_event, connection.ready_future),
                    name=f"solver-mcp-{name}",
                )
                connection.owner_task = task
                ready = connection.ready_future

        try:
            return await asyncio.wait_for(asyncio.shield(ready), timeout=self.connect_timeout)
        except TimeoutError:
            connection.error = f"{name} MCP startup timed out after {self.connect_timeout:g}s"
            if connection.state == "starting":
                connection.state = "unavailable"
            logger.warning("Solver MCP unavailable (%s): %s", name, connection.error)
            return False

    async def _connection_owner(
        self,
        connection: McpConnection,
        stop_event: asyncio.Event,
        ready_future: asyncio.Future[bool],
    ) -> None:
        """Keep each AnyIO stdio context in the same task that entered it."""
        try:
            command = str(connection.spec["command"])
            args = [str(arg) for arg in connection.spec.get("args", [])]
            env = connection.spec.get("env")
            cwd = connection.spec.get("cwd")
            params = StdioServerParameters(command=command, args=args, env=env, cwd=cwd)
            async with AsyncExitStack() as stack:
                read, write = await asyncio.wait_for(
                    stack.enter_async_context(stdio_client(params)), timeout=self.connect_timeout
                )
                session = await asyncio.wait_for(
                    stack.enter_async_context(ClientSession(read, write)), timeout=self.connect_timeout
                )
                await asyncio.wait_for(session.initialize(), timeout=self.connect_timeout)
                tools = await asyncio.wait_for(session.list_tools(), timeout=self.connect_timeout)
                tool_catalog = {
                    tool.name: {
                        "name": tool.name,
                        "description": tool.description or "",
                        "input_schema": self._tool_input_schema(tool),
                    }
                    for tool in tools.tools
                }
                if connection.name == "kali" and "server_health" in tool_catalog:
                    health = await asyncio.wait_for(
                        session.call_tool("server_health", {}), timeout=self.connect_timeout
                    )
                    health_data = self._result_data(health)
                    if self._result_is_error(health) or (
                        isinstance(health_data, dict) and health_data.get("success") is False
                    ):
                        raise ConnectionError(self._result_text(health) or "Kali health check failed")

                connection.session = session
                connection.tools = tool_catalog
                connection.state = "ready"
                connection.error = ""
                connection.generation += 1
                if not ready_future.done():
                    ready_future.set_result(True)
                logger.info(
                    "Solver MCP connected: %s (%d tools)", connection.name, len(connection.tools)
                )
                await stop_event.wait()
        except asyncio.CancelledError:
            if not ready_future.done():
                ready_future.set_result(False)
            raise
        except Exception as exc:
            connection.state = "unavailable"
            connection.error = f"{type(exc).__name__}: {exc}"
            connection.session = None
            connection.tools = {}
            if not ready_future.done():
                ready_future.set_result(False)
            logger.warning("Solver MCP unavailable (%s): %s", connection.name, exc)
        finally:
            connection.session = None
            connection.tools = {}
            if connection.state == "ready":
                connection.state = "stopped"
            if connection.owner_task is asyncio.current_task():
                connection.owner_task = None
                connection.stop_event = None
                connection.ready_future = None

    async def _disconnect(self, connection: McpConnection) -> None:
        async with connection.lock:
            task = connection.owner_task
            stop_event = connection.stop_event
            if task and not task.done() and stop_event:
                stop_event.set()
        if task and task is not asyncio.current_task():
            result = await asyncio.gather(task, return_exceptions=True)
            for error in result:
                if isinstance(error, BaseException) and not isinstance(error, asyncio.CancelledError):
                    logger.debug("MCP owner task failed while closing %s: %s", connection.name, error)
        elif not task:
            connection.session = None
            connection.tools = {}
            if connection.state != "unavailable":
                connection.state = "stopped"

    async def register_challenge(self, challenge: str, challenge_dir: str | Path) -> dict[str, Any]:
        """Schedule package extraction and analysis without delaying solver startup."""
        await self.start()
        source = Path(challenge_dir).resolve()
        if not source.is_dir():
            return {"state": "unavailable", "error": f"Challenge directory not found: {source}"}
        fingerprint = await asyncio.to_thread(self._directory_fingerprint, source / "distfiles")
        key = hashlib.sha256(f"{challenge}\0{source}\0{fingerprint}".encode()).hexdigest()[:16]
        analysis = self._challenges.get(challenge)
        if analysis and analysis.challenge_dir == source and analysis.source_fingerprint == fingerprint:
            return self.analysis_status(challenge)
        if analysis and analysis.preparation_task and not analysis.preparation_task.done():
            analysis.preparation_task.cancel()
            await asyncio.gather(analysis.preparation_task, return_exceptions=True)
            await self._drop_jadx_lease(challenge)
        work_dir = (self.runtime_root / key).resolve()
        if not work_dir.is_relative_to(self.runtime_root.resolve()):
            raise ValueError("Analysis work directory escaped the configured runtime directory")
        analysis = ChallengeAnalysis(challenge, source, work_dir, fingerprint)
        self._challenges[challenge] = analysis
        analysis.work_dir.mkdir(parents=True, exist_ok=True)
        self._persist_analysis(analysis)
        analysis.preparation_task = asyncio.create_task(
            self._prepare_challenge(analysis), name=f"analysis-prepare-{key}"
        )
        return self.analysis_status(challenge)

    async def release_challenge(self, challenge: str) -> None:
        analysis = self._challenges.get(challenge)
        task = analysis.preparation_task if analysis else None
        if task and task is not asyncio.current_task() and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await self._drop_jadx_lease(challenge)

    async def _drop_jadx_lease(self, challenge: str) -> None:
        analysis = self._challenges.get(challenge)
        if analysis:
            analysis.jadx_lease = False
        async with self._jadx_condition:
            if self._jadx_owner == challenge:
                self._jadx_owner = None
                self._jadx_condition.notify_all()

    async def _acquire_jadx_lease(self, challenge: str) -> None:
        async with self._jadx_condition:
            while self._jadx_owner not in (None, challenge):
                await self._jadx_condition.wait()
            self._jadx_owner = challenge
            analysis = self._challenges.get(challenge)
            if analysis:
                analysis.jadx_lease = True

    async def _prepare_challenge(self, analysis: ChallengeAnalysis) -> None:
        try:
            async with self._prep_lock:
                analysis.state = "starting"
                await asyncio.to_thread(self._persist_analysis, analysis)
                if analysis.work_dir.exists():
                    shutil.rmtree(analysis.work_dir)
                analysis.work_dir.mkdir(parents=True, exist_ok=True)
                candidates = await asyncio.to_thread(self._collect_analysis_files, analysis)
                analysis.files = {item.file_id: item for item in candidates}
            if not candidates:
                analysis.state = "ready"
                await asyncio.to_thread(self._persist_analysis, analysis)
                return
            analysis.state = "ready"
            ida_files = [item for item in candidates if item.kind == "binary"]
            apk_files = [item for item in candidates if item.kind == "apk"]

            async def prepare_ida(item: AnalysisFile) -> None:
                async with self._ida_preparation_limit:
                    await self._prepare_ida(analysis, item)

            await asyncio.gather(
                *(prepare_ida(item) for item in ida_files),
                return_exceptions=True,
            )
            for item in apk_files:
                await self._prepare_jadx(analysis, item)
            if apk_files and not any(item.jadx_state == "ready" for item in apk_files):
                await self._drop_jadx_lease(analysis.challenge)
            await asyncio.to_thread(self._persist_analysis, analysis)
        except asyncio.CancelledError:
            await self._drop_jadx_lease(analysis.challenge)
            raise
        except Exception as exc:
            analysis.state = "unavailable"
            analysis.error = f"{type(exc).__name__}: {exc}"
            logger.warning("Analysis preparation failed for %s: %s", analysis.challenge, exc)
            await self._drop_jadx_lease(analysis.challenge)
            await asyncio.to_thread(self._persist_analysis, analysis)

    @staticmethod
    def _directory_fingerprint(directory: Path) -> str:
        digest = hashlib.sha256()
        if not directory.is_dir():
            return digest.hexdigest()
        for path in sorted(p for p in directory.rglob("*") if p.is_file() and not p.is_symlink()):
            try:
                digest.update(path.relative_to(directory).as_posix().encode("utf-8", errors="replace"))
                digest.update(bytes.fromhex(SolverMcpGateway._sha256(path)))
            except OSError:
                continue
        return digest.hexdigest()

    @staticmethod
    def _persist_analysis(analysis: ChallengeAnalysis) -> None:
        status_file = analysis.work_dir / "status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "challenge": analysis.challenge,
            "state": analysis.state,
            "source_fingerprint": analysis.source_fingerprint,
            "error": analysis.error,
            "files": [
                {
                    "file_id": item.file_id,
                    "path": item.relative_path,
                    "sha256": item.sha256,
                    "kind": item.kind,
                    "ida_state": item.ida_state,
                    "ida_session": item.ida_session,
                    "jadx_state": item.jadx_state,
                    "error": item.error,
                }
                for item in analysis.files.values()
            ],
        }
        temporary = status_file.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(status_file)

    def _collect_analysis_files(self, analysis: ChallengeAnalysis) -> list[AnalysisFile]:
        extracted_root = analysis.work_dir / "files"
        extracted_root.mkdir(parents=True, exist_ok=True)
        distfiles = (analysis.challenge_dir / "distfiles").resolve()
        source_files = [
            p for p in distfiles.rglob("*")
            if p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(distfiles)
        ]
        materialized_bytes = sum(path.stat().st_size for path in source_files)
        if materialized_bytes > self.max_extracted_bytes:
            raise ValueError("Original attachments exceed the configured analysis size limit")
        copied: list[Path] = []
        for original in source_files:
            relative = original.relative_to(analysis.challenge_dir / "distfiles")
            destination = extracted_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
            copied.append(destination)

        entry_count = [0]
        byte_count = [materialized_bytes]
        pending = [path for path in copied if self._is_archive(path)]
        for depth in range(self.max_archive_depth):
            if not pending:
                break
            newly_copied: list[Path] = []
            for archive in pending:
                newly_copied.extend(
                    self._extract_archive(archive, extracted_root, depth + 1, byte_count, entry_count)
                )
            copied.extend(newly_copied)
            pending = [path for path in newly_copied if self._is_archive(path)]

        result: list[AnalysisFile] = []
        for path in copied:
            kind = self._file_kind(path)
            if kind == "other":
                continue
            digest = self._sha256(path)
            relative = path.relative_to(extracted_root).as_posix()
            file_id = f"{digest[:16]}:{relative}"
            item = AnalysisFile(file_id, relative, path.resolve(), digest, kind)
            if kind == "binary":
                if "ida" in self.connections:
                    item.ida_state = "queued"
                else:
                    item.error = "IDA MCP is not configured"
                    item.ida_ready_event.set()
            if kind == "apk":
                if "jadx" in self.connections:
                    item.jadx_state = "queued"
                else:
                    item.error = "JADX MCP is not configured"
                    item.jadx_ready_event.set()
            result.append(item)
        return result

    def _extract_archive(
        self,
        archive: Path,
        root: Path,
        depth: int,
        byte_count: list[int],
        entry_count: list[int],
    ) -> list[Path]:
        extracted: list[Path] = []
        base = archive.parent / f"{archive.name}.unpacked-{depth}"
        if not base.resolve().is_relative_to(root.resolve()):
            raise ValueError("Archive destination escaped the analysis directory")
        base.mkdir(parents=True, exist_ok=True)

        def destination_for(name: str) -> Path | None:
            normalized = name.replace("\\", "/")
            member = PurePosixPath(normalized)
            if member.is_absolute() or any(part in ("..", "") for part in member.parts):
                return None
            destination = (base / Path(*member.parts)).resolve()
            if not destination.is_relative_to(base.resolve()):
                return None
            return destination

        try:
            if zipfile.is_zipfile(archive):
                with zipfile.ZipFile(archive) as bundle:
                    for member in bundle.infolist():
                        entry_count[0] += 1
                        if entry_count[0] > self.max_archive_entries:
                            raise ValueError("Archive entry limit exceeded")
                        destination = destination_for(member.filename)
                        if destination is None:
                            continue
                        mode = (member.external_attr >> 16) & 0xFFFF
                        if stat.S_ISLNK(mode):
                            continue
                        if member.is_dir():
                            destination.mkdir(parents=True, exist_ok=True)
                            continue
                        if member.file_size + byte_count[0] > self.max_extracted_bytes:
                            raise ValueError("Archive extraction size limit exceeded")
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with bundle.open(member) as source, destination.open("wb") as output:
                            copied = 0
                            while chunk := source.read(1024 * 1024):
                                copied += len(chunk)
                                byte_count[0] += len(chunk)
                                if byte_count[0] > self.max_extracted_bytes:
                                    raise ValueError("Archive extraction size limit exceeded")
                                output.write(chunk)
                        if copied:
                            extracted.append(destination)
            elif tarfile.is_tarfile(archive):
                with tarfile.open(archive, "r:*") as bundle:
                    for member in bundle:
                        entry_count[0] += 1
                        if entry_count[0] > self.max_archive_entries:
                            raise ValueError("Archive entry limit exceeded")
                        destination = destination_for(member.name)
                        if destination is None:
                            continue
                        if member.isdir():
                            destination.mkdir(parents=True, exist_ok=True)
                            continue
                        if not member.isfile():
                            continue
                        if member.size + byte_count[0] > self.max_extracted_bytes:
                            raise ValueError("Archive extraction size limit exceeded")
                        source = bundle.extractfile(member)
                        if source is None:
                            continue
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with source, destination.open("wb") as output:
                            while chunk := source.read(1024 * 1024):
                                byte_count[0] += len(chunk)
                                if byte_count[0] > self.max_extracted_bytes:
                                    raise ValueError("Archive extraction size limit exceeded")
                                output.write(chunk)
                        extracted.append(destination)
        except (zipfile.BadZipFile, tarfile.ReadError, OSError) as exc:
            logger.info("Skipping unreadable archive %s: %s", archive.name, exc)
        return extracted

    @staticmethod
    def _is_archive(path: Path) -> bool:
        try:
            return SolverMcpGateway._file_kind(path) != "apk" and (
                zipfile.is_zipfile(path) or tarfile.is_tarfile(path)
            )
        except OSError:
            return False

    @staticmethod
    def _file_kind(path: Path) -> str:
        try:
            with path.open("rb") as stream:
                header = stream.read(4096)
            if zipfile.is_zipfile(path):
                try:
                    with zipfile.ZipFile(path) as archive:
                        names = set(archive.namelist())
                    if "AndroidManifest.xml" in names and any(
                        name.startswith("classes") and name.endswith(".dex") for name in names
                    ):
                        return "apk"
                except (OSError, zipfile.BadZipFile):
                    return "other"
                return "other"
            if header.startswith(b"\x7fELF") or header.startswith(b"dex\n"):
                return "binary"
            if header.startswith(b"MZ") and len(header) >= 0x40:
                return "binary"
            if header[:4] in {
                b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf",
                b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca",
            }:
                return "binary"
            if path.suffix.lower() in {".so", ".dll", ".exe", ".elf", ".dex", ".dylib", ".o"}:
                return "binary"
        except OSError:
            return "other"
        return "other"

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    async def _prepare_ida(self, analysis: ChallengeAnalysis, item: AnalysisFile) -> None:
        try:
            connection = self.connections.get("ida")
            if not connection or not await self._connect("ida"):
                item.ida_state = "unavailable"
                item.error = connection.error if connection else "IDA MCP is not configured"
                return
            item.ida_state = "starting"
            result = await asyncio.wait_for(
                self._call_raw(
                    "ida",
                    "idb_open",
                    {"input_path": str(item.path), "mode": "force_headless", "run_auto_analysis": True},
                ),
                timeout=self.tool_timeout,
            )
            data = self._result_data(result)
            session = self._find_session_id(data)
            if self._result_is_error(result) or not session:
                item.ida_state = "unavailable"
                item.error = self._result_text(result) or "IDA did not return a database session"
                return
            item.ida_session = session
            item.ida_generation = connection.generation
            item.ida_state = "ready"
        except Exception as exc:
            item.ida_state = "unavailable"
            item.error = f"{type(exc).__name__}: {exc}"
        finally:
            item.ida_ready_event.set()

    @staticmethod
    def _find_session_id(value: Any) -> str:
        if isinstance(value, dict):
            if isinstance(value.get("session_id"), str):
                return value["session_id"]
            for child in value.values():
                session = SolverMcpGateway._find_session_id(child)
                if session:
                    return session
        elif isinstance(value, list):
            for child in value:
                session = SolverMcpGateway._find_session_id(child)
                if session:
                    return session
        return ""

    async def _prepare_jadx(self, analysis: ChallengeAnalysis, item: AnalysisFile) -> None:
        if "jadx" not in self.connections:
            item.jadx_state = "unavailable"
            item.error = "JADX MCP is not configured"
            item.jadx_ready_event.set()
            return
        item.jadx_state = "queued"
        await asyncio.to_thread(self._persist_analysis, analysis)
        # A single GUI is shared. Hold a challenge lease through the swarm, and
        # use the lock for each activation/call so sessions can never cross.
        await self._acquire_jadx_lease(analysis.challenge)
        try:
            await self._acquire_jadx_lease(analysis.challenge)
            async with self._jadx_lock:
                item.jadx_state = "starting"
                await asyncio.to_thread(self._persist_analysis, analysis)
                ok = await self._activate_jadx(analysis, item)
                if not ok:
                    await asyncio.sleep(1)
                    ok = await self._activate_jadx(analysis, item)
                if ok:
                    item.jadx_state = "ready"
                else:
                    item.jadx_state = "unavailable"
                    item.error = self.connections["jadx"].error or "JADX could not load this APK"
        except Exception as exc:
            item.jadx_state = "unavailable"
            item.error = f"{type(exc).__name__}: {exc}"
        finally:
            item.jadx_ready_event.set()

    async def _activate_jadx(self, analysis: ChallengeAnalysis, item: AnalysisFile) -> bool:
        item_path = str(item.path.resolve())
        if (
            self._jadx_active_file == item_path
            and self.connections["jadx"].session
            and self._jadx_process
            and self._jadx_process.returncode is None
        ):
            return True
        connection = self.connections["jadx"]
        await self._disconnect(connection)
        await self._stop_jadx_gui()
        gui = self.jadx_gui_spec
        gui_command = str(gui.get("command", "")) if isinstance(gui, dict) else ""
        if not gui_command:
            connection.state = "unavailable"
            connection.error = "No jadx_gui.command configured"
            return False
        args = [str(arg).replace("{file}", str(item.path)) for arg in gui.get("args", [])]
        if not any("{file}" in str(arg) for arg in gui.get("args", [])):
            args.append(str(item.path))
        try:
            self._jadx_process = await asyncio.create_subprocess_exec(
                gui_command,
                *args,
                cwd=gui.get("cwd"),
                env={**os.environ, **{str(k): str(v) for k, v in gui.get("env", {}).items()}},
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            if not await self._connect("jadx"):
                await self._stop_jadx_gui()
                return False
            if not await self._wait_jadx_loaded(analysis, item):
                connection.error = "JADX plugin did not confirm the requested APK"
                await self._disconnect(connection)
                connection.state = "unavailable"
                await self._stop_jadx_gui()
                return False
            self._jadx_active_file = item_path
            return True
        except Exception as exc:
            connection.state = "unavailable"
            connection.error = f"{type(exc).__name__}: {exc}"
            await self._disconnect(connection)
            await self._stop_jadx_gui()
            logger.warning("Could not launch JADX for %s: %s", item.relative_path, exc)
            return False

    async def _wait_jadx_loaded(self, analysis: ChallengeAnalysis, item: AnalysisFile) -> bool:
        # Confirm through real plugin data, not the MCP process/health endpoint.
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.jadx_ready_timeout
        while (remaining := deadline - loop.time()) > 0:
            if self._jadx_process and self._jadx_process.returncode is not None:
                return False
            try:
                result = await asyncio.wait_for(
                    self._call_raw("jadx", "get_android_manifest", {}),
                    timeout=min(10.0, remaining),
                )
                data = self._result_data(result)
                if not self._result_is_error(result) and self._manifest_matches(data, item.path):
                    return True
            except Exception:
                pass
            await asyncio.sleep(min(2.0, max(0.0, deadline - loop.time())))
        return False

    @staticmethod
    def _manifest_matches(data: Any, apk: Path) -> bool:
        expected = SolverMcpGateway._apk_package(apk)
        if not expected:
            return False
        if not isinstance(data, dict):
            data = {"content": str(data)}
        text = json.dumps(data, ensure_ascii=False, default=str)
        if not text or '"error"' in text:
            return False
        live = SolverMcpGateway._find_manifest_package(data)
        return live == expected

    @staticmethod
    def _find_manifest_package(value: Any) -> str:
        import re

        if isinstance(value, dict):
            direct = value.get("package")
            if isinstance(direct, str) and direct:
                return direct
            for child in value.values():
                package = SolverMcpGateway._find_manifest_package(child)
                if package:
                    return package
        elif isinstance(value, list):
            for child in value:
                package = SolverMcpGateway._find_manifest_package(child)
                if package:
                    return package
        elif isinstance(value, str):
            match = re.search(
                r"(?:\bpackage\s*=\s*['\"]|['\"]package['\"]\s*:\s*['\"])([^'\"]+)",
                value,
            )
            if match:
                return match.group(1)
        return ""

    @staticmethod
    def _apk_package(apk: Path) -> str:
        try:
            with zipfile.ZipFile(apk) as archive:
                raw = archive.read("AndroidManifest.xml")
        except (OSError, zipfile.BadZipFile):
            return ""
        import re
        text = raw.decode("utf-8", errors="ignore")
        match = re.search(r"\bpackage\s*=\s*['\"]([^'\"]+)['\"]", text)
        if match:
            return match.group(1)
        try:
            return SolverMcpGateway._package_from_binary_manifest(raw)
        except (IndexError, struct.error, UnicodeDecodeError, ValueError):
            return ""

    @staticmethod
    def _package_from_binary_manifest(data: bytes) -> str:
        import struct

        strings: list[str] = []

        def read_length8(buffer: bytes, offset: int) -> tuple[int, int]:
            first = buffer[offset]
            offset += 1
            if first & 0x80:
                second = buffer[offset]
                offset += 1
                return ((first & 0x7F) << 8) | second, offset
            return first, offset

        def read_length16(buffer: bytes, offset: int) -> tuple[int, int]:
            value = struct.unpack_from("<H", buffer, offset)[0]
            offset += 2
            if value & 0x8000:
                second = struct.unpack_from("<H", buffer, offset)[0]
                offset += 2
                return ((value & 0x7FFF) << 16) | second, offset
            return value, offset

        offset = 0
        if len(data) >= 8 and struct.unpack_from("<H", data, 0)[0] == 0x0003:
            offset = struct.unpack_from("<H", data, 2)[0]
        while offset + 8 <= len(data):
            chunk_type, header_size, chunk_size = struct.unpack_from("<HHI", data, offset)
            if chunk_size < 8 or offset + chunk_size > len(data):
                break
            if chunk_type == 0x0001:
                string_count, style_count, flags, strings_start, _ = struct.unpack_from("<IIIII", data, offset + 8)
                offsets_start = offset + header_size
                utf8 = bool(flags & 0x100)
                for index in range(string_count):
                    string_offset = struct.unpack_from("<I", data, offsets_start + 4 * index)[0]
                    pos = offset + strings_start + string_offset
                    if utf8:
                        _, pos = read_length8(data, pos)
                        byte_length, pos = read_length8(data, pos)
                        strings.append(data[pos:pos + byte_length].decode("utf-8", errors="replace"))
                    else:
                        char_length, pos = read_length16(data, pos)
                        strings.append(data[pos:pos + char_length * 2].decode("utf-16le", errors="replace"))
            elif chunk_type == 0x0102 and strings:
                ext = offset + 16
                name_index = struct.unpack_from("<I", data, ext + 4)[0]
                if name_index >= len(strings) or strings[name_index] != "manifest":
                    offset += chunk_size
                    continue
                attr_start, attr_size, attr_count = struct.unpack_from("<HHH", data, ext + 8)
                attr_offset = ext + attr_start
                for index in range(attr_count):
                    attr = attr_offset + index * attr_size
                    name_index, raw_index = struct.unpack_from("<II", data, attr + 4)[0], struct.unpack_from("<I", data, attr + 8)[0]
                    if name_index < len(strings) and strings[name_index] == "package":
                        if raw_index != 0xFFFFFFFF and raw_index < len(strings):
                            return strings[raw_index]
                        value_type = data[attr + 15]
                        value_data = struct.unpack_from("<I", data, attr + 16)[0]
                        if value_type == 0x03 and value_data < len(strings):
                            return strings[value_data]
                        return ""
            offset += chunk_size
        return ""

    async def _stop_jadx_gui(self) -> None:
        process, self._jadx_process = self._jadx_process, None
        self._jadx_active_file = ""
        if not process or process.returncode is not None:
            return
        if os.name == "nt":
            try:
                killer = await asyncio.create_subprocess_exec(
                    "taskkill", "/PID", str(process.pid), "/T", "/F",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await asyncio.wait_for(killer.wait(), timeout=10)
            except Exception:
                process.kill()
        else:
            process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except TimeoutError:
            process.kill()
            await process.wait()

    async def list_analysis_tools(self, challenge: str) -> dict[str, Any]:
        analysis = self._challenges.get(challenge)
        if not analysis:
            return {"challenge": challenge, "tools": [], "status": self.analysis_status(challenge)}
        result: list[dict[str, Any]] = []
        for server_name, connection in self.connections.items():
            if connection.state != "ready":
                continue
            eligible = [
                item for item in analysis.files.values()
                if (server_name == "ida" and item.kind == "binary" and item.ida_state == "ready")
                or (server_name == "jadx" and item.kind == "apk" and item.jadx_state == "ready")
            ]
            if server_name != "kali" and not eligible:
                continue
            for tool in connection.tools.values():
                if server_name == "ida" and tool["name"] in {"idb_open", "idb_list"}:
                    continue
                public_tool = dict(tool)
                if server_name == "ida":
                    schema = dict(public_tool.get("input_schema") or {})
                    properties = dict(schema.get("properties") or {})
                    properties.pop("database", None)
                    schema["properties"] = properties
                    if isinstance(schema.get("required"), list):
                        schema["required"] = [
                            name for name in schema["required"] if name != "database"
                        ]
                    public_tool["input_schema"] = schema
                result.append(
                    {
                        "server": server_name,
                        **public_tool,
                        "file_ids": [item.file_id for item in eligible] if server_name != "kali" else [],
                    }
                )
        return {"challenge": challenge, "tools": result, "status": self.analysis_status(challenge)}

    async def call_analysis_tool(
        self,
        challenge: str,
        server: str,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        file_id: str = "",
    ) -> dict[str, Any]:
        connection = self.connections.get(server)
        if server == "ida" and tool_name in {"idb_open", "idb_list"}:
            return {"ok": False, "error": "IDA session management is reserved for the gateway."}
        args = dict(arguments or {})
        analysis = self._challenges.get(challenge)
        item: AnalysisFile | None = None
        if server in {"ida", "jadx"}:
            item = analysis.files.get(file_id) if analysis else None
            kind = "binary" if server == "ida" else "apk"
            if not item or item.kind != kind:
                return {"ok": False, "error": "Unknown or incompatible analysis file_id"}
            try:
                ready_event = item.ida_ready_event if server == "ida" else item.jadx_ready_event
                await asyncio.wait_for(ready_event.wait(), timeout=self.tool_timeout)
                self._require_file(challenge, file_id, kind, server)
            except (TimeoutError, ValueError, OSError) as exc:
                return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

        if not connection or connection.state != "ready":
            return {"ok": False, "error": f"MCP server '{server}' is unavailable", "status": self.analysis_status(challenge)}
        if tool_name not in connection.tools:
            return {"ok": False, "error": f"Unknown MCP tool {server}.{tool_name}"}
        if server == "ida" and item:
            args.pop("database", None)
            args["database"] = item.ida_session
        elif server == "jadx":
            try:
                await asyncio.wait_for(self._acquire_jadx_lease(challenge), timeout=self.tool_timeout)
            except TimeoutError:
                return {"ok": False, "error": "JADX is still assigned to another challenge; retry later"}

        lock = self._jadx_lock if server == "jadx" else connection.call_lock
        async with lock:
            if server == "ida" and item and analysis and item.ida_generation != connection.generation:
                await self._prepare_ida(analysis, item)
                if item.ida_state != "ready":
                    return {"ok": False, "error": item.error or "IDA session recovery failed"}
                args["database"] = item.ida_session
            if server == "jadx" and item and analysis:
                needs_activation = (
                    self._jadx_active_file != str(item.path.resolve())
                    or not self._jadx_process
                    or self._jadx_process.returncode is not None
                )
                if needs_activation and not await self._activate_jadx(analysis, item):
                    return {"ok": False, "error": connection.error or "JADX activation failed"}
            try:
                result = await asyncio.wait_for(
                    self._call_raw(server, tool_name, args), timeout=self.tool_timeout
                )
                if self._result_is_error(result):
                    return {"ok": False, "error": self._result_text(result)[:1000] or "MCP tool returned an error"}
                data = self._bounded_data(self._result_data(result))
                return {"ok": True, "result": data, "text": self._result_text(result)[:MAX_TOOL_RESULT_CHARS]}
            except Exception as exc:
                logger.warning("MCP tool failed %s.%s: %s", server, tool_name, exc)
                if server == "jadx":
                    await self._disconnect(connection)
                    await self._stop_jadx_gui()
                    analysis = self._challenges.get(challenge)
                    item = analysis.files.get(file_id) if analysis else None
                    if analysis and item and await self._activate_jadx(analysis, item):
                        try:
                            retried = await asyncio.wait_for(self._call_raw(server, tool_name, args), timeout=self.tool_timeout)
                            if self._result_is_error(retried):
                                raise RuntimeError(self._result_text(retried)[:1000] or "MCP retry returned an error")
                            return {"ok": True, "result": self._bounded_data(self._result_data(retried)), "text": self._result_text(retried)[:MAX_TOOL_RESULT_CHARS], "retried": True}
                        except Exception as retry_exc:
                            exc = retry_exc
                else:
                    await self._disconnect(connection)
                    if await self._connect(server):
                        try:
                            if server == "ida" and item and analysis:
                                await self._prepare_ida(analysis, item)
                                if item.ida_state != "ready":
                                    return {"ok": False, "error": item.error or "IDA session recovery failed"}
                                args["database"] = item.ida_session
                            retried = await asyncio.wait_for(self._call_raw(server, tool_name, args), timeout=self.tool_timeout)
                            if self._result_is_error(retried):
                                return {"ok": False, "error": self._result_text(retried)[:1000] or "MCP retry returned an error"}
                            return {"ok": True, "result": self._bounded_data(self._result_data(retried)), "text": self._result_text(retried)[:MAX_TOOL_RESULT_CHARS], "retried": True}
                        except Exception as retry_exc:
                            exc = retry_exc
                return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    def _require_file(self, challenge: str, file_id: str, kind: str, server: str) -> AnalysisFile:
        analysis = self._challenges.get(challenge)
        if not analysis:
            raise ValueError(f"No analysis session for challenge {challenge!r}")
        item = analysis.files.get(file_id)
        if not item or item.kind != kind:
            raise ValueError("Unknown or incompatible analysis file_id")
        state = item.ida_state if server == "ida" else item.jadx_state
        if state != "ready":
            raise ValueError(f"{server} session is {state}: {item.error}")
        if self._sha256(item.path) != item.sha256:
            raise ValueError("Analysis file changed after its session was created")
        return item

    async def _call_raw(self, server: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        connection = self.connections[server]
        if not connection.session and not await self._connect(server):
            raise ConnectionError(connection.error or f"{server} unavailable")
        session = connection.session
        if session is None:
            raise ConnectionError(connection.error or f"{server} session is unavailable")
        if tool_name not in connection.tools:
            raise ValueError(f"Unknown MCP tool {server}.{tool_name}")
        return await session.call_tool(tool_name, arguments)

    def analysis_status(self, challenge: str | None = None) -> dict[str, Any]:
        servers = {
            name: {
                "state": item.state,
                "error": item.error,
                "tools": sorted(
                    tool for tool in item.tools
                    if name != "ida" or tool not in {"idb_open", "idb_list"}
                ),
            }
            for name, item in self.connections.items()
        }
        challenges = self._challenges.values() if challenge is None else [self._challenges.get(challenge)]
        entries = []
        for analysis in challenges:
            if not analysis:
                continue
            entries.append(
                {
                    "challenge": analysis.challenge,
                    "state": analysis.state,
                    "error": analysis.error,
                    "files": [
                        {
                            "file_id": file.file_id,
                            "path": file.relative_path,
                            "sha256": file.sha256,
                            "kind": file.kind,
                            "ida": {"state": file.ida_state, "bound": bool(file.ida_session)},
                            "jadx": {"state": file.jadx_state},
                            "error": file.error,
                        }
                        for file in analysis.files.values()
                    ],
                }
            )
        return {"servers": servers, "challenges": entries}

    @staticmethod
    def _result_data(result: Any) -> Any:
        structured = getattr(result, "structured_content", None)
        if structured is not None:
            return structured
        content = getattr(result, "content", [])
        text_items = [item.text for item in content if getattr(item, "type", "") == "text"]
        text = "\n".join(text_items)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text

    @staticmethod
    def _tool_input_schema(tool: Any) -> dict[str, Any]:
        schema = getattr(tool, "input_schema", None)
        return schema if isinstance(schema, dict) else {}

    @staticmethod
    def _bounded_data(data: Any) -> Any:
        serialized = json.dumps(data, ensure_ascii=False, default=str)
        if len(serialized) <= MAX_TOOL_RESULT_CHARS:
            return data
        return {
            "truncated": True,
            "preview": serialized[:MAX_TOOL_RESULT_CHARS],
            "original_chars": len(serialized),
        }

    @classmethod
    def _result_text(cls, result: Any) -> str:
        data = cls._result_data(result)
        if isinstance(data, str):
            return data
        return json.dumps(data, ensure_ascii=False, default=str)

    @staticmethod
    def _result_is_error(result: Any) -> bool:
        is_error = getattr(result, "is_error", False)
        if bool(is_error):
            return True
        data = SolverMcpGateway._result_data(result)
        if isinstance(data, dict):
            return "error" in data or data.get("success") is False
        if isinstance(data, str):
            lowered = data.lstrip().lower()
            return lowered.startswith(("error:", "invalid params:", "tool error:", "exception:"))
        return False


def make_claude_analysis_server(gateway: SolverMcpGateway, challenge: str) -> Any:
    """Build the same three generic broker tools for Claude Agent SDK."""
    from claude_agent_sdk import create_sdk_mcp_server, tool

    schema = {"type": "object", "properties": {}, "additionalProperties": False}

    @tool("list_analysis_tools", "List MCP tools ready for this challenge. Returns per-file IDs for IDA/JADX.", schema)
    async def list_tools(_: dict[str, Any]) -> dict[str, Any]:
        data = await gateway.list_analysis_tools(challenge)
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}]}

    @tool("analysis_status", "Show MCP server and reverse-engineering session readiness for this challenge.", schema)
    async def status(_: dict[str, Any]) -> dict[str, Any]:
        data = gateway.analysis_status(challenge)
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}]}

    call_schema = {
        "type": "object",
        "properties": {
            "server": {"type": "string", "enum": ["ida", "jadx", "kali"]},
            "tool_name": {"type": "string"},
            "arguments": {"type": "object", "additionalProperties": True},
            "file_id": {"type": "string", "description": "Required for IDA and JADX; omit for Kali."},
        },
        "required": ["server", "tool_name"],
        "additionalProperties": False,
    }

    @tool("call_analysis_tool", "Call one ready IDA, JADX, or Kali MCP tool for this challenge.", call_schema)
    async def call_tool(args: dict[str, Any]) -> dict[str, Any]:
        data = await gateway.call_analysis_tool(
            challenge,
            str(args.get("server", "")),
            str(args.get("tool_name", "")),
            args.get("arguments") or {},
            str(args.get("file_id", "")),
        )
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}]}

    return create_sdk_mcp_server("analysis", tools=[list_tools, call_tool, status])
