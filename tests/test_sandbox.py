from __future__ import annotations

import pytest

from backend.sandbox import ChallengeNotReadyError, DockerSandbox


@pytest.mark.asyncio
async def test_write_file_uses_container_posix_path_on_windows(tmp_path):
    calls = []

    class FakeContainer:
        async def put_archive(self, path, archive):
            calls.append(path)

    sandbox = DockerSandbox(image="unused", challenge_dir=str(tmp_path))
    sandbox._container = FakeContainer()
    await sandbox.write_file("/challenge/workspace/knowledge/test.py", b"print('ok')")
    assert calls == ["/challenge/workspace/knowledge"]


@pytest.mark.asyncio
async def test_invalid_package_releases_workspace_and_docker_client(tmp_path, monkeypatch):
    closed = []

    class FakeDocker:
        async def close(self):
            closed.append(True)

    monkeypatch.setattr("backend.sandbox.aiodocker.Docker", FakeDocker)
    sandbox = DockerSandbox(image="unused", challenge_dir=str(tmp_path))
    with pytest.raises(ChallengeNotReadyError, match="no attachment or remote environment"):
        await sandbox.start()
    assert closed == [True]
    assert sandbox.workspace_dir == ""
    assert sandbox._docker is None


@pytest.mark.asyncio
async def test_failed_container_start_removes_created_container(tmp_path, monkeypatch):
    (tmp_path / "distfiles").mkdir()
    (tmp_path / "distfiles" / "input.txt").write_text("fixture", encoding="utf-8")
    deleted = []
    closed = []

    class FakeContainer:
        async def start(self):
            raise RuntimeError("Docker start failed")

        async def delete(self, force):
            deleted.append(force)

    class FakeContainers:
        async def create(self, config):
            return FakeContainer()

    class FakeDocker:
        containers = FakeContainers()

        async def close(self):
            closed.append(True)

    monkeypatch.setattr("backend.sandbox.aiodocker.Docker", FakeDocker)
    sandbox = DockerSandbox(image="unused", challenge_dir=str(tmp_path))
    with pytest.raises(RuntimeError, match="Docker start failed"):
        await sandbox.start()
    assert deleted == [True]
    assert closed == [True]
    assert sandbox.workspace_dir == ""
    assert sandbox._container is None
    assert sandbox._tracked is False
