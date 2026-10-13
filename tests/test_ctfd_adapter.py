from __future__ import annotations

from types import SimpleNamespace

import pytest
import yaml

from backend.ctfd import CTFdClient
from backend.platforms.ctfd_legacy import CTFdLegacyAdapter


class FakeCTFdClient:
    base_url = "https://ctfd.example"
    token = "fixture"
    _logged_in = False

    def __init__(self) -> None:
        self.pull_count = 0

    async def fetch_all_challenges(self):
        return [{"id": 7, "name": "State Test", "category": "misc", "value": 100}]

    async def pull_challenge(self, challenge, output_dir):
        from pathlib import Path

        self.pull_count += 1
        directory = Path(output_dir) / "state-test"
        (directory / "distfiles").mkdir(parents=True, exist_ok=True)
        (directory / "distfiles" / "fixture.txt").write_text("fixture", encoding="utf-8")
        return str(directory)

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_solve_status_fetch_failure_is_not_reported_as_zero_solved(monkeypatch):
    client = CTFdClient("https://ctfd.example", token="fixture")

    async def failing_get(path):
        raise RuntimeError("upstream unavailable")

    monkeypatch.setattr(client, "_get", failing_get)
    with pytest.raises(RuntimeError, match="Could not fetch solved challenges"):
        await client.fetch_solved_names()


@pytest.mark.asyncio
async def test_state_queries_do_not_redownload_or_reset_needs_input(tmp_path):
    client = FakeCTFdClient()
    adapter = CTFdLegacyAdapter(
        client,
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(
            challenge_state_db_path=str(tmp_path / "state.sqlite3"),
            challenge_run_id="ctfd-state-test",
        ),
    )
    try:
        await adapter.prepare_challenge("7")
        assert client.pull_count == 1
        assert (await adapter.get_challenge_state("State Test"))["state"] == "ready"
        await adapter.mark_needs_input("State Test", "operator review")
        state = await adapter.get_challenge_state("State Test")
        assert state["state"] == "needs_input"
        assert state["reason"] == "operator review"
        assert client.pull_count == 1
        await adapter.retry_challenge_preparation("State Test")
        assert (await adapter.get_challenge_state("State Test"))["state"] == "waiting_for_decision"
        assert client.pull_count == 1
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_ctfd_slug_collisions_fail_before_download(tmp_path):
    client = FakeCTFdClient()

    async def colliding_challenges():
        return [{"id": 1, "name": "A.B"}, {"id": 2, "name": "AB"}]

    client.fetch_all_challenges = colliding_challenges
    adapter = CTFdLegacyAdapter(
        client,
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        with pytest.raises(ValueError, match="collide after directory normalization"):
            await adapter.list_challenges()
        assert client.pull_count == 0
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_ctfd_downloads_all_declared_files_with_unique_names_and_utf8(tmp_path, monkeypatch):
    client = CTFdClient(base_url="https://ctfd.example", token="fixture")
    urls = []

    class Response:
        content = b"fresh"

        def raise_for_status(self):
            pass

    class HTTP:
        async def get(self, url, **kwargs):
            urls.append(url)
            return Response()

    async def logged_in():
        pass

    async def http_client():
        return HTTP()

    monkeypatch.setattr(client, "_ensure_logged_in", logged_in)
    monkeypatch.setattr(client, "_ensure_client", http_client)
    directory = await client.pull_challenge(
        {
            "id": 1,
            "name": "中文题目",
            "files": ["/files/one/data.bin", "/files/two/data.bin"],
        },
        str(tmp_path),
    )
    from pathlib import Path

    root = Path(directory)
    metadata = yaml.safe_load((root / "metadata.yml").read_text(encoding="utf-8"))
    assert metadata["name"] == "中文题目"
    assert len(metadata["files"]) == 2
    assert len(set(metadata["files"])) == 2
    assert all((root / filename).read_bytes() == b"fresh" for filename in metadata["files"])
    assert len(urls) == 2


@pytest.mark.asyncio
async def test_ctfd_download_failure_marks_package_needs_input(tmp_path):
    class FailedClient(FakeCTFdClient):
        async def pull_challenge(self, challenge, output_dir):
            raise RuntimeError("attachment request failed")

    client = FailedClient()
    adapter = CTFdLegacyAdapter(
        client,
        str(tmp_path / "challenges"),
        settings=SimpleNamespace(challenge_state_db_path=str(tmp_path / "state.sqlite3")),
    )
    try:
        with pytest.raises(RuntimeError, match="attachment request failed"):
            await adapter.prepare_challenge("7")
        state = adapter.state.get_challenge("7")
        assert state is not None
        assert state["state"] == "needs_input"
        assert "attachment request failed" in state["reason"]
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_ctfd_stale_cached_file_cannot_mask_failed_redownload(tmp_path, monkeypatch):
    client = CTFdClient(base_url="https://ctfd.example", token="fixture")
    stale = tmp_path / "stale" / "distfiles" / "payload.bin"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"old")

    class HTTP:
        async def get(self, url, **kwargs):
            raise ConnectionError("network unavailable")

    async def logged_in():
        pass

    async def http_client():
        return HTTP()

    monkeypatch.setattr(client, "_ensure_logged_in", logged_in)
    monkeypatch.setattr(client, "_ensure_client", http_client)
    with pytest.raises(RuntimeError, match="Failed to download CTFd attachment"):
        await client.pull_challenge(
            {"id": 1, "name": "stale", "files": ["/files/payload.bin"]},
            str(tmp_path),
        )
    assert stale.read_bytes() == b"old"
