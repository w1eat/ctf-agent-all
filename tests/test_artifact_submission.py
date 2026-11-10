from types import SimpleNamespace

import pytest

from backend.tools.core import do_submit_artifact


@pytest.mark.asyncio
async def test_artifact_submission_reads_full_sandbox_file_and_respects_dry_run():
    calls = []
    source = "x" * 30000

    class Sandbox:
        async def read_file(self, path):
            assert path == "/challenge/workspace/solve.py"
            return source

    class Platform:
        async def submit_artifact(self, name, fields):
            calls.append((name, fields))
            return SimpleNamespace(display="pending")

    assert await do_submit_artifact(Platform(), Sandbox(), "demo", {"code": "/challenge/workspace/solve.py"}, {"requirements": "lib"}, True) == "DRY RUN — artifact not submitted."
    assert not calls
    assert await do_submit_artifact(Platform(), Sandbox(), "demo", {"code": "/challenge/workspace/solve.py"}, {"requirements": "lib"}) == "pending"
    assert calls == [("demo", {"code": source, "requirements": "lib"})]
    result = await do_submit_artifact(Platform(), Sandbox(), "demo", {"code": "/challenge/workspace/../secret"}, {})
    assert "must be under" in result
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_upload_is_staged_for_browser_and_removed_after_submission():
    from pathlib import Path

    staged = []

    class Sandbox:
        async def read_file(self, path):
            return b"\x00\xffbinary"

    class Platform:
        async def submit_artifact(self, name, fields, uploads):
            path = Path(uploads["archive"])
            staged.append(path)
            assert path.name == "run.zip"
            assert path.read_bytes() == b"\x00\xffbinary"
            return SimpleNamespace(display="pending")

    result = await do_submit_artifact(Platform(), Sandbox(), "demo", {}, {}, uploads={"archive": "/challenge/workspace/run.zip"})
    assert result == "pending"
    assert not staged[0].exists()
