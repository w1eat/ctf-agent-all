from __future__ import annotations

import json
import shlex
import subprocess
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.prompts import ChallengeMeta
from backend.writeups import WriteupManager, capture_exp_files


@pytest.fixture(autouse=True)
def isolated_knowledge_inbox(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.local_knowledge.KNOWLEDGE_INBOX_DIR", tmp_path / "knowledge-inbox")


def settings(**overrides):
    values = {
        "challenge_run_id": "run-1",
        "flag_verification_quorum": 2,
        "writeup_model_spec": "",
        "writeup_timeout_seconds": 5,
        "writeup_replay_timeout_seconds": 5,
        "sandbox_image": "fake",
        "container_memory_limit": "1g",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def solver_result(flag="FLAG{ok}", **overrides):
    values = {
        "flag": flag,
        "status": "verified",
        "verified_by": ("solver-a", "solver-b"),
        "findings_summary": "解码附件中的隐藏数据",
        "solution_steps": ("读取附件", "解码数据并提取 Flag"),
        "evidence": ("输出包含目标字符串",),
        "saved_exp_paths": (),
        "exp_run_command": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def install_writer(monkeypatch, *, fail=False):
    module = types.ModuleType("backend.writeup_writer")

    async def write_solution_sections(_settings, _model_spec, context):
        if fail:
            raise RuntimeError("writer unavailable")
        assert "trace" not in context
        return {
            "principle": "从题目数据恢复原文。",
            "steps": ["读取输入", "运行解码脚本"],
            "exp_usage": "运行保存的脚本。",
            "limitations": "需要题目附件。",
        }

    module.write_solution_sections = write_solution_sections
    monkeypatch.setitem(sys.modules, "backend.writeup_writer", module)
    return module


def manifest(challenge: Path):
    return json.loads((challenge / "solution" / "manifest.json").read_text(encoding="utf-8"))


def test_capture_exp_restricts_paths_symlinks_size_and_credentials(tmp_path):
    challenge = tmp_path / "challenge"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    script = workspace / "solve.py"
    script.write_text("print('FLAG{' + 'ok}')\n", encoding="utf-8")
    sandbox = SimpleNamespace(workspace_dir=str(workspace))

    saved = capture_exp_files(challenge, sandbox, ["/challenge/workspace/solve.py"], "FLAG{ok}", "solver-a")
    assert len(saved) == 1
    assert (challenge / saved[0]).read_text(encoding="utf-8") == script.read_text(encoding="utf-8")
    assert capture_exp_files(challenge, sandbox, ["solve.py"], "FLAG{ok}", "solver-a") == saved

    for unsafe in ("../solve.py", "/challenge/distfiles/solve.py", "x/../solve.py", "C:\\solve.py"):
        with pytest.raises(ValueError):
            capture_exp_files(challenge, sandbox, [unsafe], "FLAG{ok}", "solver-a")
    (workspace / "large.py").write_bytes(b"A" * (256 * 1024 + 1))
    with pytest.raises(ValueError):
        capture_exp_files(challenge, sandbox, ["large.py"], "FLAG{ok}", "solver-a")
    (workspace / "secret.py").write_text("API_KEY=supersecret\n", encoding="utf-8")
    with pytest.raises(ValueError):
        capture_exp_files(challenge, sandbox, ["secret.py"], "FLAG{ok}", "solver-a")
    (workspace / "hardcoded.py").write_text("print('FLAG{ok}')\n", encoding="utf-8")
    with pytest.raises(ValueError):
        capture_exp_files(challenge, sandbox, ["hardcoded.py"], "FLAG{ok}", "solver-a")
    try:
        (workspace / "link.py").symlink_to(script)
    except (OSError, NotImplementedError):
        pass
    else:
        with pytest.raises(ValueError):
            capture_exp_files(challenge, sandbox, ["link.py"], "FLAG{ok}", "solver-a")


@pytest.mark.asyncio
async def test_only_confirmed_matching_flags_schedule(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    manager = WriteupManager(settings(), default_model_spec="test/model")
    meta = ChallengeMeta(name="demo", category="crypto")
    challenge = tmp_path / "challenge"
    candidate = solver_result(status="candidate_found", verified_by=("solver-a",))

    assert await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "independent_quorum", candidate) is None
    assert await manager.record_and_schedule(challenge, meta, "FLAG{other}", "platform_confirmed", solver_result()) is None
    assert not (challenge / "solution" / "manifest.json").exists()

    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "independent_quorum", solver_result())
    await manager.wait_for_pending()
    data = manifest(challenge)
    assert data["status"] == "complete"
    assert data["records"][0]["run_id"] == "run-1"
    assert data["records"][0]["verified_by"] == ["solver-a", "solver-b"]
    assert "独立复核，未必提交" in (challenge / "writeup.md").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_platform_priority_manual_and_redaction(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    manager = WriteupManager(settings(), default_model_spec="test/model")
    challenge = tmp_path / "challenge"
    meta = ChallengeMeta(name="demo", category="misc", description="Authorization: Bearer abcsecret")
    result = solver_result(evidence=("Cookie: sid=abcsecret", "password=abcsecret"))
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "independent_quorum", result)
    await manager.wait_for_pending()
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", solver_result())
    await manager.wait_for_pending()
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "independent_quorum", result)
    await manager.wait_for_pending()

    text = (challenge / "writeup.md").read_text(encoding="utf-8")
    assert "平台确认" in text
    assert "人工复现" in text
    assert "FLAG{ok}" in text
    assert "abcsecret" not in text
    assert manifest(challenge)["current_key"].endswith("platform_confirmed")


@pytest.mark.asyncio
async def test_coordinator_confirmation_without_method_needs_review(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    manager = WriteupManager(settings(), default_model_spec="test/model")
    challenge = tmp_path / "challenge"
    await manager.record_and_schedule(
        challenge, ChallengeMeta(name="direct"), "FLAG{ok}", "platform_confirmed", evidence=("accepted",)
    )
    await manager.wait_for_pending()
    assert manifest(challenge)["status"] == "needs_review"
    assert "待补充" in (challenge / "writeup.md").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_unverified_candidate_writeup_is_created_and_later_upgraded(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    challenge = tmp_path / "candidate"
    challenge.mkdir()
    manager = WriteupManager(settings(), default_model_spec="deepseek/deepseek-flash")

    async def replay_must_not_run(*_args, **_kwargs):
        raise AssertionError("Candidate writeup should not wait for verification replay")

    monkeypatch.setattr(manager, "_replay", replay_must_not_run)
    meta = ChallengeMeta(name="candidate", category="pwn")
    candidate = solver_result(status="candidate_found")

    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "candidate_found", candidate)
    await manager.wait_for_pending()
    text = (challenge / "writeup.md").read_text(encoding="utf-8")
    assert "候选 Flag（未经确认）" in text
    assert "尚未经过平台或独立验证" in text
    assert "未执行复现" in text
    assert manifest(challenge)["records"][0]["confirmation_source"] == "candidate_found"

    async def manual_replay(*_args, **_kwargs):
        return {"status": "manual", "reason": "No executable EXP", "command": "",
                "exit_code": None, "stdout": "", "stderr": ""}

    monkeypatch.setattr(manager, "_replay", manual_replay)
    confirmed = solver_result()
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", confirmed)
    await manager.wait_for_pending()
    text = (challenge / "writeup.md").read_text(encoding="utf-8")
    assert "平台确认" in text
    assert "尚未经过平台或独立验证" not in text

    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "candidate_found", candidate)
    await manager.wait_for_pending()
    assert "平台确认" in (challenge / "writeup.md").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_replay_uses_saved_script_and_arguments(tmp_path, monkeypatch):
    install_writer(monkeypatch)

    class FakeSandbox:
        def __init__(self, **_kwargs):
            self.workspace_dir = ""

        async def start(self):
            self.workspace_dir = str(tmp_path / "replay")
            Path(self.workspace_dir).mkdir(exist_ok=True)

        async def exec(self, command, timeout_s):
            assert timeout_s == 5
            args = shlex.split(command.split("&&", 1)[1].strip())
            script = Path(self.workspace_dir) / args[1]
            process = subprocess.run(
                [sys.executable, str(script), *args[2:]], capture_output=True, text=True, check=False
            )
            return SimpleNamespace(exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)

        async def stop(self):
            pass

    monkeypatch.setattr("backend.writeups.DockerSandbox", FakeSandbox)
    challenge = tmp_path / "challenge"
    workspace = tmp_path / "original"
    workspace.mkdir()
    (workspace / "solve.py").write_text("import sys\nprint('FLAG{' + sys.argv[-1] + '}')\n", encoding="utf-8")
    saved = capture_exp_files(challenge, SimpleNamespace(workspace_dir=str(workspace)), ["solve.py"], "FLAG{ok}", "solver-a")
    result = solver_result(saved_exp_paths=saved, exp_run_command="python3 /challenge/workspace/solve.py ok")
    manager = WriteupManager(settings(), default_model_spec="test/model")
    await manager.record_and_schedule(challenge, ChallengeMeta(name="demo"), "FLAG{ok}", "platform_confirmed", result)
    await manager.wait_for_pending()

    data = manifest(challenge)
    assert data["status"] == "complete"
    assert data["records"][0]["replay"]["status"] == "verified"
    assert (challenge / "exp" / "solve.py").is_file()
    assert "自动复现通过" in (challenge / "writeup.md").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_writer_failure_retries_and_manual_edit_is_preserved(tmp_path, monkeypatch):
    module = install_writer(monkeypatch, fail=True)
    manager = WriteupManager(settings(), default_model_spec="test/model")
    challenge = tmp_path / "challenge"
    meta = ChallengeMeta(name="demo")
    result = solver_result()
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", result)
    await manager.wait_for_pending()
    assert manifest(challenge)["status"] == "failed"

    async def good_writer(_settings, _model_spec, _context):
        return {"principle": "原理", "steps": ["步骤"], "exp_usage": "手动运行", "limitations": "无"}

    module.write_solution_sections = good_writer
    await manager.resume_pending(tmp_path)
    await manager.wait_for_pending()
    assert manifest(challenge)["status"] == "complete"
    writeup = challenge / "writeup.md"
    writeup.write_text("人工编辑", encoding="utf-8")
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", result)
    await manager.wait_for_pending()
    assert writeup.read_text(encoding="utf-8") == "人工编辑"
    assert manifest(challenge)["status"] == "needs_review"
    override_manager = WriteupManager(settings(writeup_model_spec="deepseek/deepseek-flash"))
    await override_manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", result)
    await override_manager.wait_for_pending()
    assert writeup.read_text(encoding="utf-8") == "人工编辑"
    assert manifest(challenge)["status"] == "needs_review"
    await manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", result, force=True)
    await manager.wait_for_pending()
    assert "# demo 题解" in writeup.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_coordinator_confirmation_uses_prior_solver_or_first_solver(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    manager = WriteupManager(settings(), default_model_spec="openai/first-solver")
    meta = ChallengeMeta(name="demo")
    challenge = tmp_path / "with-candidate"

    await manager.record_and_schedule(
        challenge, meta, "FLAG{ok}", "candidate_found",
        solver_result(status="candidate_found"), model_spec="deepseek/deepseek-flash",
    )
    await manager.wait_for_pending()
    await manager.record_and_schedule(
        challenge, meta, "FLAG{ok}", "platform_confirmed", evidence=("accepted",),
    )
    await manager.wait_for_pending()
    current = next(item for item in manifest(challenge)["records"] if item["confirmation_source"] == "platform_confirmed")
    assert current["model_spec"] == "deepseek/deepseek-flash"

    direct = tmp_path / "direct-confirmation"
    await manager.record_and_schedule(direct, meta, "FLAG{direct}", "platform_confirmed", evidence=("accepted",))
    await manager.wait_for_pending()
    assert manifest(direct)["records"][0]["model_spec"] == "openai/first-solver"


@pytest.mark.asyncio
async def test_explicit_writeup_model_wins_for_new_record(tmp_path, monkeypatch):
    install_writer(monkeypatch)
    manager = WriteupManager(settings(writeup_model_spec="deepseek/deepseek-flash"), default_model_spec="openai/first-solver")
    challenge = tmp_path / "challenge"
    await manager.record_and_schedule(
        challenge, ChallengeMeta(name="demo"), "FLAG{ok}", "candidate_found",
        solver_result(status="candidate_found"), model_spec="claude-sdk/claude-opus-4-6",
    )
    await manager.wait_for_pending()
    assert manifest(challenge)["records"][0]["model_spec"] == "deepseek/deepseek-flash"


@pytest.mark.asyncio
@pytest.mark.parametrize("original_status", ["pending", "failed"])
async def test_resume_uses_explicit_model_for_unfinished_records(tmp_path, monkeypatch, original_status):
    module = install_writer(monkeypatch, fail=True)
    challenge = tmp_path / "challenge"
    meta = ChallengeMeta(name="demo")
    result = solver_result()
    old_manager = WriteupManager(settings(), default_model_spec="claude-sdk/claude-opus-4-6")
    await old_manager.record_and_schedule(challenge, meta, "FLAG{ok}", "platform_confirmed", result)
    await old_manager.wait_for_pending()
    assert manifest(challenge)["status"] == "failed"
    if original_status == "pending":
        data = manifest(challenge)
        data["status"] = data["records"][0]["status"] = "pending"
        (challenge / "solution" / "manifest.json").write_text(json.dumps(data), encoding="utf-8")

    used_models = []

    async def good_writer(_settings, model_spec, _context):
        used_models.append(model_spec)
        return {"principle": "原理", "steps": ["步骤"], "exp_usage": "手动运行", "limitations": "无"}

    module.write_solution_sections = good_writer
    current_manager = WriteupManager(settings(writeup_model_spec="deepseek/deepseek-flash"))
    await current_manager.resume_pending(tmp_path)
    await current_manager.wait_for_pending()
    current = manifest(challenge)["records"][0]
    assert used_models == ["deepseek/deepseek-flash"]
    assert current["model_spec"] == "deepseek/deepseek-flash"
    assert current["status"] == "complete"

    later_manager = WriteupManager(settings(writeup_model_spec="openai/another-model"))
    await later_manager.resume_pending(tmp_path)
    await later_manager.wait_for_pending()
    assert manifest(challenge)["records"][0]["model_spec"] == "deepseek/deepseek-flash"
    assert used_models == ["deepseek/deepseek-flash"]
