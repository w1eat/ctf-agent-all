"""Evidence survives cleanup, remains auditable, and never implies flag proof."""

from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import struct
import zlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.platforms.browser_mcp import BrowserAutoPlatformAdapter
from backend.prompts import ChallengeMeta
from backend.tracing import SolverTracer
from backend.writeup_evidence import (
    EvidenceRecorder,
    capture_artifact_files,
    evidence_context,
    load_command_evidence,
    safe_path,
    store_artifact,
    validated_artifacts,
)
from backend.writeups import WriteupManager, capture_exp_files


def png(pixel: bytes = b"\0\0\0\xff") -> bytes:
    def chunk(kind, content):
        return struct.pack(">I", len(content)) + kind + content + struct.pack(">I", zlib.crc32(kind + content) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\0" + pixel)) + chunk(b"IEND", b""))


PNG = png()


def test_durable_journal_preserves_output_redacts_secrets_and_pairs_concurrent_calls(tmp_path):
    tracer = SolverTracer("demo", "model", log_dir=str(tmp_path / "logs"),
                          challenge_dir=str(tmp_path / "challenge"), run_id="run-a")
    tracer.tool_call("Bash", {"command": "first", "cwd": "/challenge/workspace"}, 1, call_id="call-a")
    tracer.tool_call("Bash", {"command": "second"}, 2, call_id="call-b")
    tracer.tool_result("Bash", "second output", 2, call_id="call-b")
    output = "x" * 5000 + "\nCookie: sid=private-cookie\nEND-OF-REAL-OUTPUT"
    tracer.tool_result("Bash", output, 2, call_id="call-a")
    tracer.close()

    rows = load_command_evidence(tmp_path / "challenge", [tracer.evidence_log_path], run_id="run-a")
    first = next(row for row in rows if row["command"] == "first")
    assert first["step"] == 1
    assert first["cwd"] == "/challenge/workspace"
    assert first["output"].endswith("END-OF-REAL-OUTPUT")
    assert "private-cookie" not in first["output"]
    assert load_command_evidence(tmp_path / "challenge", [tracer.evidence_log_path], run_id="other-run") == []
    trace = Path(tracer.path).read_text(encoding="utf-8")
    assert "END-OF-REAL-OUTPUT" not in trace  # Legacy display trace stays small.


def test_evidence_selection_keeps_early_middle_and_final_derivations(tmp_path):
    recorder = EvidenceRecorder(tmp_path, "model", "run-a")
    for step in range(1, 61):
        recorder.call("bash", {"command": f"step-{step}"}, step)
        recorder.result("bash", f"observed-{step}", step)
    rows = load_command_evidence(tmp_path, [recorder.relative_path], run_id="run-a", limit=12)
    assert len(rows) == 12
    assert rows[0]["step"] == 1
    assert rows[-1]["step"] == 60
    assert any(25 <= row["step"] <= 35 for row in rows)


def test_command_parameters_preserve_zero_and_false(tmp_path):
    recorder = EvidenceRecorder(tmp_path, "model", "run-a")
    recorder.call("analysis", {"offset": 0, "enabled": False}, 1)
    recorder.result("analysis", "observed", 1)
    row = load_command_evidence(tmp_path, [recorder.relative_path], run_id="run-a")[0]
    assert row["arguments"] == {"offset": 0, "enabled": False}


@pytest.mark.asyncio
async def test_native_command_output_is_recorded_before_tool_display_truncation(tmp_path):
    from backend.tools.core import do_bash

    recorder = EvidenceRecorder(tmp_path, "model", "run-a")

    async def worker(step):
        output = "x" * 25_000 + f"END-{step}"

        async def execute(*args, **kwargs):
            await asyncio.sleep(0)
            return SimpleNamespace(stdout=output, stderr="", exit_code=0)

        recorder.call("bash", {"command": "same command"}, step)
        with evidence_context(recorder, "bash", step):
            display = await do_bash(SimpleNamespace(exec=execute), "same command")
        recorder.result("bash", display, step)
        assert f"END-{step}" not in display

    await asyncio.gather(worker(1), worker(2))
    rows = load_command_evidence(tmp_path, [recorder.relative_path], run_id="run-a")
    assert {row["step"]: row["output"][-5:] for row in rows} == {1: "END-1", 2: "END-2"}
    assert all(row["exit_code"] == 0 for row in rows)


@pytest.mark.asyncio
async def test_new_evidence_supersedes_inflight_generation_and_refreshes_completed_candidate(tmp_path, monkeypatch):
    from backend import writeup_writer

    entered, release = asyncio.Event(), asyncio.Event()
    seen = []

    async def writer(_settings, _model, context):
        seen.append(context["findings_summary"])
        if len(seen) == 1:
            entered.set()
            await release.wait()
        return {"principle": context["findings_summary"], "steps": ["核对真实证据"],
                "exp_usage": "人工查看图片。", "limitations": "候选未经确认。"}

    monkeypatch.setattr(writeup_writer, "write_solution_sections", writer)
    settings = SimpleNamespace(challenge_run_id="run-a", sandbox_image="fake", writeup_timeout_seconds=5)
    manager = WriteupManager(settings, default_model_spec="test/model")
    meta = ChallengeMeta(name="demo")
    first = SimpleNamespace(flag="FLAG{ok}", findings_summary="早期发现")
    await manager.record_and_schedule(tmp_path, meta, "FLAG{ok}", "candidate_found", first)
    await asyncio.wait_for(entered.wait(), timeout=2)
    artifact = store_artifact(tmp_path, PNG, "first.png", source="solver", run_id="run-a")
    second = SimpleNamespace(flag="FLAG{ok}", findings_summary="补充关键图片", saved_artifacts=(artifact,))
    await manager.record_and_schedule(tmp_path, meta, "FLAG{ok}", "candidate_found", second)
    release.set()
    await manager.wait_for_pending()
    text = (tmp_path / "writeup.md").read_text(encoding="utf-8")
    assert "补充关键图片" in text and "早期发现" not in text
    assert "![" in text and seen == ["早期发现", "补充关键图片"]
    additional = store_artifact(tmp_path, png(b"\xff\0\0\xff"), "second.png", source="solver", run_id="run-a")
    third = SimpleNamespace(flag="FLAG{ok}", findings_summary="最终补充证据", saved_artifacts=(additional,))
    await manager.record_and_schedule(tmp_path, meta, "FLAG{ok}", "candidate_found", third)
    await manager.wait_for_pending()
    text = (tmp_path / "writeup.md").read_text(encoding="utf-8")
    assert "最终补充证据" in text and text.count("![") == 2


@pytest.mark.asyncio
async def test_refresh_preserves_published_exp_identity(tmp_path, monkeypatch):
    from backend import writeup_writer

    async def writer(*args):
        return {"principle": "从脚本恢复数据。", "steps": ["运行真实脚本"],
                "exp_usage": "python3 solve.py", "limitations": "候选待确认。"}

    monkeypatch.setattr(writeup_writer, "write_solution_sections", writer)
    challenge, workspace = tmp_path / "challenge", tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "solve.py").write_text("print('computed value')\n", encoding="utf-8")
    saved = capture_exp_files(challenge, SimpleNamespace(workspace_dir=str(workspace)), ["solve.py"], "FLAG{ok}", "model")
    manager = WriteupManager(SimpleNamespace(challenge_run_id="run-a", sandbox_image="fake", writeup_timeout_seconds=5),
                             default_model_spec="test/model")
    result = SimpleNamespace(flag="FLAG{ok}", findings_summary="从脚本恢复数据。", saved_exp_paths=saved,
                             exp_run_command="python3 solve.py")
    await manager.record_and_schedule(challenge, ChallengeMeta(name="demo"), "FLAG{ok}", "candidate_found", result)
    await manager.wait_for_pending()
    artifact = store_artifact(challenge, PNG, "result.png", source="model", run_id="run-a")
    result.saved_artifacts = (artifact,)
    await manager.record_and_schedule(challenge, ChallengeMeta(name="demo"), "FLAG{ok}", "candidate_found", result)
    await manager.wait_for_pending()
    state = json.loads((challenge / "solution/manifest.json").read_text(encoding="utf-8"))
    record = state["records"][0]
    assert record["exp_sha256"]["exp/solve.py"] == hashlib.sha256((challenge / "exp/solve.py").read_bytes()).hexdigest()
    assert "人工作出修改" not in record["replay"]["reason"]


def test_artifact_capture_is_binary_safe_bounded_and_detects_tampering(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "recovered.png").write_bytes(PNG)
    (workspace / "notes.txt").write_text("Cookie: sid=private-cookie\nuseful result", encoding="utf-8")
    (workspace / "bad.png").write_bytes(b"this is not a PNG")
    challenge = tmp_path / "challenge"
    saved, issues = capture_artifact_files(challenge, SimpleNamespace(workspace_dir=str(workspace)),
        ["/challenge/workspace/recovered.png", "notes.txt", "bad.png", "../outside.png"], source="solver", run_id="run-a")
    assert len(saved) == 2
    assert len(issues) == 2
    assert (challenge / saved[0]["path"]).read_bytes() == PNG
    assert "private-cookie" not in (challenge / saved[1]["path"]).read_text(encoding="utf-8")
    assert validated_artifacts(challenge, saved) == saved
    (challenge / saved[0]["path"]).write_bytes(PNG + b"changed")
    assert [item["media_type"] for item in validated_artifacts(challenge, saved)] == ["text/plain"]


def test_artifact_capture_rejects_links_and_oversized_files(tmp_path, monkeypatch):
    from backend import writeup_evidence

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "large.png").write_bytes(PNG)
    monkeypatch.setattr(writeup_evidence, "MAX_ARTIFACT_BYTES", 20)
    saved, issues = capture_artifact_files(tmp_path / "challenge", SimpleNamespace(workspace_dir=str(workspace)),
        ["large.png"], source="solver")
    assert not saved and issues
    for raw in ("../escape.png", "/absolute.png", "C:/escape.png", "a/../../escape.png", "a\\escape.png"):
        with pytest.raises(ValueError):
            safe_path(workspace, raw, must_exist=False)
    try:
        (workspace / "link.png").symlink_to(workspace / "large.png")
    except (OSError, NotImplementedError):
        return
    with pytest.raises(ValueError):
        safe_path(workspace, "link.png")


@pytest.mark.asyncio
async def test_replay_archives_media_before_cleanup_without_claiming_flag_verification(tmp_path, monkeypatch):
    from backend import writeup_writer

    workspace = tmp_path / "solver-workspace"
    workspace.mkdir()
    (workspace / "solve.py").write_text("# real decoding script\n", encoding="utf-8")
    challenge = tmp_path / "challenge"
    (challenge / "distfiles").mkdir(parents=True)
    (challenge / "distfiles" / "input.bin").write_bytes(b"challenge-input")
    saved = capture_exp_files(challenge, SimpleNamespace(workspace_dir=str(workspace)), ["solve.py"], "FLAG{ok}", "solver-a")
    settings = SimpleNamespace(challenge_run_id="run-a", sandbox_image="fake", writeup_timeout_seconds=5,
                               writeup_replay_timeout_seconds=5, flag_verification_quorum=2)
    observed = {}

    class Sandbox:
        def __init__(self, **kwargs):
            self.workspace_dir = str(tmp_path / "replay")

        async def start(self):
            Path(self.workspace_dir).mkdir()

        async def exec(self, command, timeout_s):
            (Path(self.workspace_dir) / "recovered.png").write_bytes(PNG)
            return SimpleNamespace(exit_code=0, stdout="image successfully recovered", stderr="")

        async def stop(self):
            shutil.rmtree(self.workspace_dir)
            observed["stopped"] = True

    async def writer(_settings, _model, context):
        assert observed["stopped"]
        observed["artifact"] = context["artifacts"][0]
        assert context["replay"]["status"] == "artifacts_generated"
        assert context["environment"]["inputs"][0]["sha256"] == hashlib.sha256(b"challenge-input").hexdigest()
        return {
            "principle": "恢复图片后人工读取文本。", "steps": ["运行解码器", "检查图片"],
            "environment": ["需要题目附件"], "exp_usage": "运行保存的脚本。", "limitations": "未自动识别 Flag。",
            "detailed_steps": [{"title": "查看恢复的图片", "explanation": "根据实际生成的图片核对隐藏文本。",
                                "expected_result": "人工核对 Flag。", "evidence_ids": [],
                                "artifact_ids": [context["artifacts"][0]["id"]]}],
        }

    monkeypatch.setattr("backend.writeups.DockerSandbox", Sandbox)
    monkeypatch.setattr(writeup_writer, "write_solution_sections", writer)
    manager = WriteupManager(settings, default_model_spec="test/model")
    await manager.record_and_schedule(challenge, ChallengeMeta(name="media", category="forensics"), "FLAG{ok}",
        "platform_confirmed", SimpleNamespace(flag="FLAG{ok}", findings_summary="图片恢复",
                                              saved_exp_paths=saved, exp_run_command="python3 solve.py"))
    await manager.wait_for_pending()
    state = json.loads((challenge / "solution/manifest.json").read_text(encoding="utf-8"))
    assert state["status"] == "needs_review"
    record = state["records"][0]
    assert record["replay"]["status"] == "artifacts_generated"
    assert (challenge / observed["artifact"]["path"]).read_bytes() == PNG
    assert (challenge / record["replay"]["evidence_path"]).is_file()
    text = (challenge / "writeup.md").read_text(encoding="utf-8")
    assert "![" in text and observed["artifact"]["path"] in text
    assert "产物已生成，待人工核对" in text
    assert "自动复现通过" not in text
    assert "image successfully recovered" in text


def test_renderer_rejects_invented_evidence_and_escapes_code_fences(tmp_path):
    manager = WriteupManager(SimpleNamespace(sandbox_image="fake"))
    record = {"challenge": {"name": "demo", "category": "misc"}, "flag": "FLAG{ok}",
              "confirmation_source": "platform_confirmed", "solution_steps": ["步骤"],
              "findings_summary": "原理", "evidence": [], "saved_artifacts": []}
    replay = {"status": "manual", "reason": "需人工复现", "command": ""}
    step = {"title": "步骤", "explanation": "解释", "expected_result": "结果", "evidence_ids": ["invented"], "artifact_ids": []}
    with pytest.raises(ValueError, match="not supplied"):
        manager._render(record, {"steps": ["步骤"], "detailed_steps": [step]}, replay, [], tmp_path)
    row = {"id": "real-command", "command": "printf demo", "output": "~~~\nunaltered-output",
           "journal_path": "solution/evidence/demo/commands.jsonl"}
    text = manager._render(record, {"steps": ["步骤"]}, replay, [], tmp_path, commands=[row])
    assert "~~~~text\n~~~\nunaltered-output\n~~~~" in text


@pytest.mark.asyncio
@pytest.mark.parametrize("screenshot_result", ["saved", "missing", "error"])
async def test_submission_evidence_preserves_actual_screenshot_or_text_fallback(
    tmp_path, monkeypatch, caplog, screenshot_result,
):
    adapter = BrowserAutoPlatformAdapter.__new__(BrowserAutoPlatformAdapter)
    challenge = tmp_path / "challenge"
    downloads = tmp_path / "download 证据" / "run-a"
    browser_cwd = tmp_path / "browser working directory"
    browser_cwd.mkdir()
    monkeypatch.chdir(browser_cwd)
    adapter._directories = {"demo": challenge}
    adapter.state = SimpleNamespace(run_id="run-a")

    async def call(name, args):
        assert name == "browser_take_screenshot"
        if screenshot_result == "error":
            return "ERROR\nScreenshot capture failed"
        if screenshot_result == "saved":
            Path(args["filename"]).write_bytes(PNG)
        return "saved"

    adapter.browser = SimpleNamespace(download_dir=downloads, call=call)
    await adapter._archive_submission_evidence(SimpleNamespace(name="demo"), "FLAG{ok}", "Correct\nCookie: private-cookie")
    digest = hashlib.sha256(b"FLAG{ok}").hexdigest()
    record = json.loads((challenge / f"solution/submissions/{digest[:20]}.json").read_text(encoding="utf-8"))
    artifacts = validated_artifacts(challenge, record["artifacts"])
    assert len(artifacts) == (2 if screenshot_result == "saved" else 1)
    assert record["flag_sha256"] == digest
    text = next(item for item in artifacts if item["media_type"] == "text/plain")
    assert "private-cookie" not in (challenge / text["path"]).read_text(encoding="utf-8")
    if screenshot_result == "saved":
        screenshot = next(item for item in artifacts if item["kind"] == "screenshot")
        assert (challenge / screenshot["path"]).read_bytes() == PNG
        assert len(list(downloads.glob("submission-*.png"))) == 1
        assert not list(browser_cwd.glob("submission-*.png"))
    elif screenshot_result == "error":
        assert "Screenshot capture failed" in caplog.text
