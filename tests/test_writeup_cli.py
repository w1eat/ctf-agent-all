"""Historical backfill distinguishes unverified candidates from confirmations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from backend import writeup_cli


def _challenge(root: Path, name: str = "Test Challenge") -> Path:
    path = root / "test-challenge"
    path.mkdir(parents=True)
    (path / "metadata.yml").write_text(
        f"name: {name}\ncategory: crypto\ndescription: Decode the ciphertext\n",
        encoding="utf-8",
    )
    return path


def _jsonl(path: Path, *events: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")


def test_scoped_trace_accepts_candidate_but_keeps_unscoped_traces_out(tmp_path: Path) -> None:
    challenge_root = tmp_path / "challenges"
    _challenge(challenge_root)
    logs = tmp_path / "logs"
    _jsonl(
        logs / "trace-solved.jsonl",
        {"type": "start", "challenge": "Test Challenge", "model": "gpt-5.4", "run_id": "run-one"},
        {"type": "tool_result", "result": "Recovered the AES key from the supplied binary"},
        {"type": "finish", "status": "flag_found", "confirmed": True, "flag": "FLAG{correct}", "run_id": "run-one"},
    )
    _jsonl(
        logs / "trace-candidate.jsonl",
        {"type": "start", "challenge": "Test Challenge", "run_id": "run-one"},
        {"type": "model_response", "text": "Guessed from filename without a verification step"},
        {"type": "finish", "status": "candidate_found", "confirmed": False, "flag": "FLAG{guess}", "run_id": "run-one"},
    )
    _jsonl(
        logs / "trace-other-run.jsonl",
        {"type": "start", "challenge": "Test Challenge", "run_id": "run-two"},
        {"type": "model_response", "text": "Factored an RSA modulus in another competition run"},
        {"type": "finish", "status": "flag_found", "confirmed": True, "flag": "FLAG{other}", "run_id": "run-two"},
    )
    candidates, _ = writeup_cli.discover_candidates("run-one", challenge_root, logs)
    assert sorted((item.flag, item.source) for item in candidates) == [
        ("FLAG{correct}", "platform_confirmed"),
        ("FLAG{guess}", "candidate_found"),
    ]


def test_coordinator_exact_confirmation_binds_legacy_trace(tmp_path: Path) -> None:
    root = tmp_path / "challenges"
    _challenge(root)
    logs = tmp_path / "logs"
    _jsonl(
        logs / "trace-old.jsonl",
        {"type": "start", "challenge": "Test Challenge", "model": "gpt-5.4"},
        {"type": "model_response", "text": "Used a known-plaintext attack to recover the encryption key"},
        {"type": "finish", "status": "flag_found", "confirmed": True, "flag": "FLAG{exact}"},
    )
    _jsonl(
        logs / "coordinator-run-one-20260101.jsonl",
        {"type": "tool_call", "tool": "mcp__coordinator__confirm_submission", "args": json.dumps({
            "challenge_name": "Test Challenge", "flag": "FLAG{exact}", "accepted": True, "reason": "Page accepted the flag"
        })},
        {"type": "tool_result", "tool": "mcp__coordinator__confirm_submission", "result": {
            "content": [{"type": "text", "text": 'CORRECT — Agent confirmed "FLAG{exact}": Page accepted the flag'}]
        }},
    )
    candidates, _ = writeup_cli.discover_candidates("run-one", root, logs)
    assert len(candidates) == 1
    assert candidates[0].flag == "FLAG{exact}"
    assert "known-plaintext" in " ".join(candidates[0].evidence)
    assert writeup_cli.discover_candidates("run-two", root, logs)[0] == []


def test_manifest_quorum_and_path_safety(tmp_path: Path) -> None:
    root = tmp_path / "challenges"
    challenge = _challenge(root)
    logs = tmp_path / "logs"
    solution = challenge / "solution"
    solution.mkdir()
    (solution / "manifest.json").write_text(json.dumps({"records": [
        {
            "run_id": "run-one", "flag": "FLAG{quorum}",
            "confirmation_source": "independent_quorum",
            "verified_by": ["solver-A", "solver-B"],
            "evidence": ["Two independent solvers recovered the same decryption key"],
            "status": "failed",
        },
        {
            "run_id": "run-one", "flag": "FLAG{candidate}",
            "confirmation_source": "candidate_found", "evidence": ["long evidence text"],
        },
        {
            "run_id": "run-two", "flag": "FLAG{other}",
            "confirmation_source": "platform_confirmed", "evidence": ["valid but other run"],
        },
    ]}), encoding="utf-8")
    candidates, _ = writeup_cli.discover_candidates("run-one", root, logs)
    assert sorted((item.flag, item.source) for item in candidates) == [
        ("FLAG{candidate}", "candidate_found"),
        ("FLAG{quorum}", "independent_quorum"),
    ]
    assert not writeup_cli._saved_file_exists(challenge, "../../etc/passwd")
    assert not writeup_cli._saved_file_exists(challenge, "/etc/passwd")


def test_cli_rejects_unsafe_run_id() -> None:
    result = CliRunner().invoke(writeup_cli.main, ["backfill", "--run-id", "../other"])
    assert result.exit_code != 0
    assert "run ID" in result.output


@pytest.mark.asyncio
async def test_backfill_schedules_manifest_and_waits(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = tmp_path / "challenges"
    challenge = _challenge(root)
    solution = challenge / "solution"
    solution.mkdir()
    (solution / "manifest.json").write_text(json.dumps({"records": [{
        "run_id": "run-one", "flag": "FLAG{verified}",
        "confirmation_source": "independent_quorum", "verified_by": ["A", "B"],
        "solution_steps": ["The script decrypts the binary using the recovered key"],
        "status": "failed",
    }]}), encoding="utf-8")
    calls: list[tuple[str, str]] = []

    class FakeManager:
        def __init__(self, settings, default_model_spec=""):
            assert settings.challenge_run_id == "run-one"

        async def record_and_schedule(self, challenge_dir, meta, flag, source, **kwargs):
            assert kwargs["solver_result"].verified_by == ("A", "B")
            calls.append((flag, source))
            return Path(challenge_dir) / "writeup.md"

        async def wait_for_pending(self, timeout=180):
            calls.append(("wait", ""))

    monkeypatch.setattr(writeup_cli, "WriteupManager", FakeManager)
    count, _ = await writeup_cli.run_backfill("run-one", root, tmp_path / "logs", model_spec="openai/test")
    assert count == 1
    assert calls == [("FLAG{verified}", "independent_quorum"), ("wait", "")]


@pytest.mark.asyncio
async def test_backfill_schedules_run_scoped_unverified_candidate(monkeypatch, tmp_path: Path):
    root = tmp_path / "challenges"
    _challenge(root)
    logs = tmp_path / "logs"
    _jsonl(
        logs / "trace-candidate.jsonl",
        {"type": "start", "challenge": "Test Challenge", "run_id": "candidate-run"},
        {"type": "model_response", "text": "Recovered the exact candidate from the service output"},
        {"type": "finish", "status": "candidate_found", "confirmed": False,
         "flag": "FLAG{candidate}", "run_id": "candidate-run"},
    )
    calls = []

    class Manager:
        def __init__(self, settings, default_model_spec=""):
            pass

        async def record_and_schedule(self, challenge_dir, meta, flag, source, **kwargs):
            calls.append((flag, source, kwargs["solver_result"].status))
            return Path(challenge_dir) / "writeup.md"

        async def wait_for_pending(self, timeout=180):
            pass

    monkeypatch.setattr(writeup_cli, "WriteupManager", Manager)
    count, _ = await writeup_cli.run_backfill(
        "candidate-run", root, logs, model_spec="deepseek/deepseek-flash"
    )
    assert count == 1
    assert calls == [("FLAG{candidate}", "candidate_found", "candidate_found")]


@pytest.mark.asyncio
async def test_backfill_can_upgrade_existing_candidate_writeup(monkeypatch, tmp_path: Path):
    root = tmp_path / "challenges"
    challenge = _challenge(root)
    solution = challenge / "solution"
    solution.mkdir()
    (solution / "manifest.json").write_text(json.dumps({
        "current_key": "candidate-record", "records": [
            {"key": "candidate-record", "run_id": "run-one", "flag": "FLAG{ok}",
             "confirmation_source": "candidate_found", "status": "complete",
             "findings_summary": "Recovered the flag by decoding the attachment"},
        ],
    }), encoding="utf-8")
    (challenge / "writeup.md").write_text("old candidate writeup", encoding="utf-8")
    _jsonl(
        tmp_path / "logs" / "trace-confirmed.jsonl",
        {"type": "start", "challenge": "Test Challenge", "run_id": "run-one"},
        {"type": "model_response", "text": "Recovered the flag by decoding the attachment"},
        {"type": "finish", "status": "flag_found", "confirmed": True,
         "flag": "FLAG{ok}", "run_id": "run-one"},
    )
    calls = []

    class Manager:
        def __init__(self, settings, default_model_spec=""):
            pass

        async def record_and_schedule(self, challenge_dir, meta, flag, source, **kwargs):
            calls.append(source)
            return Path(challenge_dir) / "writeup.md"

        async def wait_for_pending(self, timeout=180):
            pass

    monkeypatch.setattr(writeup_cli, "WriteupManager", Manager)
    count, _ = await writeup_cli.run_backfill(
        "run-one", root, tmp_path / "logs", model_spec="deepseek/deepseek-flash"
    )
    assert count == 1
    assert calls == ["platform_confirmed"]
