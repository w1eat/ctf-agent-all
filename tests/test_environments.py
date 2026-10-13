from __future__ import annotations

import pytest

from backend.platforms.environments import LocalEnvironmentManager


@pytest.mark.asyncio
async def test_failed_health_check_rolls_back_compose_project(tmp_path, monkeypatch):
    compose = tmp_path / "compose.yml"
    compose.write_text("services:\n  web:\n    image: nginx\n", encoding="utf-8")
    manager = LocalEnvironmentManager(tmp_path)
    commands = []

    async def fake_compose(path, project, *args):
        commands.append(("up", project, args))
        return ""

    async def bad_health(url):
        raise RuntimeError("health check failed")

    class DownProcess:
        returncode = 0

        async def communicate(self):
            return b"", b""

    async def fake_subprocess(*args, **kwargs):
        commands.append(("down", args, kwargs))
        return DownProcess()

    monkeypatch.setattr(manager, "_compose", fake_compose)
    monkeypatch.setattr(manager, "wait_healthy", bad_health)
    monkeypatch.setattr("backend.platforms.environments.asyncio.create_subprocess_exec", fake_subprocess)

    with pytest.raises(RuntimeError, match="health check failed"):
        await manager.start("demo", {"compose_file": "compose.yml", "url": "http://localhost/"})
    assert [item[0] for item in commands] == ["up", "down"]
    assert manager._projects == {}
    assert manager._compose_files == {}


@pytest.mark.asyncio
async def test_failed_compose_down_keeps_project_for_retry(tmp_path, monkeypatch):
    compose = tmp_path / "compose.yml"
    compose.write_text("services:\n  web:\n    image: nginx\n", encoding="utf-8")
    manager = LocalEnvironmentManager(tmp_path)
    manager._projects["demo"] = "ctfagent-demo"
    manager._compose_files["demo"] = compose

    class FailedProcess:
        returncode = 1

        async def communicate(self):
            return b"", b"compose down failed"

    async def fake_subprocess(*args, **kwargs):
        return FailedProcess()

    monkeypatch.setattr("backend.platforms.environments.asyncio.create_subprocess_exec", fake_subprocess)
    with pytest.raises(RuntimeError, match="compose down failed"):
        await manager.stop("demo")
    assert manager._projects == {"demo": "ctfagent-demo"}
