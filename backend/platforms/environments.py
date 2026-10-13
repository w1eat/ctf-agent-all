"""Controlled local challenge-environment lifecycle."""

from __future__ import annotations

import asyncio
import logging
import re
import uuid
from pathlib import Path
from typing import Any

import httpx
import yaml

from backend.platforms.models import EnvironmentInfo

logger = logging.getLogger(__name__)


class LocalEnvironmentManager:
    """Start only constrained Compose environments under the challenge root."""

    def __init__(self, challenges_root: str | Path, timeout_seconds: int = 60) -> None:
        self.root = Path(challenges_root).resolve()
        self.timeout_seconds = timeout_seconds
        self._projects: dict[str, str] = {}
        self._compose_files: dict[str, Path] = {}

    def _resolve_compose(self, env: dict[str, Any]) -> Path:
        raw = env.get("compose_file") or env.get("docker_compose")
        if not raw:
            raise RuntimeError("Local environment is missing compose_file")
        raw_path = Path(str(raw))
        if raw_path.is_absolute():
            path = raw_path.resolve()
        else:
            base = self.root / str(env.get("challenge_dir", ""))
            path = (base / raw_path).resolve()
        if self.root not in path.parents and path != self.root:
            raise RuntimeError("compose_file must be inside the challenges directory")
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    @staticmethod
    def validate_compose(path: Path) -> dict[str, Any]:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        services = data.get("services", {})
        if not isinstance(services, dict) or not services:
            raise RuntimeError("Compose file has no services")
        forbidden_keys = {"privileged", "network_mode", "pid", "ipc", "devices", "cap_add", "cap_additions"}
        for name, service in services.items():
            if not isinstance(service, dict):
                raise RuntimeError(f"Invalid compose service: {name}")
            for key in forbidden_keys:
                if service.get(key):
                    raise RuntimeError(f"Compose service {name!r} uses forbidden option {key!r}")
            for volume in service.get("volumes", []) or []:
                if isinstance(volume, dict):
                    if str(volume.get("type", "")).casefold() == "bind":
                        raise RuntimeError(f"Host bind mount is forbidden in service {name!r}")
                    continue
                if not isinstance(volume, str):
                    raise RuntimeError(f"Invalid volume in service {name!r}")
                source = volume.split(":", 1)[0]
                # A short-syntax source containing a path separator, drive prefix, or
                # leading dot is a host path. Plain names remain valid named volumes.
                is_windows_path = bool(re.match(r"^[A-Za-z]:[\\/]", volume))
                is_host_path = (
                    source.startswith((".", "/", "\\"))
                    or "/" in source
                    or "\\" in source
                    or is_windows_path
                )
                if source and is_host_path:
                    raise RuntimeError(f"Host bind mount is forbidden in service {name!r}")
        return data

    async def _compose(self, compose: Path, project: str, *args: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            "docker", "compose", "-f", str(compose), "-p", project, *args,
            cwd=str(compose.parent),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        if proc.returncode != 0:
            raise RuntimeError((stderr or stdout).decode("utf-8", errors="replace")[-4000:])
        return stdout.decode("utf-8", errors="replace")

    async def start(self, challenge_name: str, env: dict[str, Any]) -> EnvironmentInfo:
        if challenge_name in self._projects:
            raise RuntimeError(f"Environment already started for {challenge_name!r}")
        compose = self._resolve_compose(env)
        self.validate_compose(compose)
        project = "ctfagent-" + re.sub(r"[^a-z0-9]+", "-", challenge_name.lower()).strip("-")[:24]
        project = f"{project}-{uuid.uuid4().hex[:8]}"
        self._projects[challenge_name] = project
        self._compose_files[challenge_name] = compose
        url = str(env.get("url", ""))
        try:
            await self._compose(compose, project, "up", "-d", "--remove-orphans")
            if url:
                await self.wait_healthy(url)
        except BaseException:
            try:
                await self.stop(challenge_name)
            except Exception as cleanup_error:
                logger.warning("Could not roll back environment %s: %s", challenge_name, cleanup_error)
            raise
        return EnvironmentInfo(
            status="ready",
            source="compose",
            url=url,
            host=str(env.get("host", "")),
            port=int(env["port"]) if env.get("port") is not None else None,
            compose_project=project,
        )

    async def wait_healthy(self, url: str, attempts: int = 20) -> None:
        async with httpx.AsyncClient(verify=False, timeout=3) as client:
            for _ in range(attempts):
                try:
                    response = await client.get(url)
                    if response.status_code < 500:
                        return
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(1)
        raise RuntimeError(f"Environment did not become healthy: {url}")

    async def stop(self, challenge_name: str) -> None:
        project = self._projects.get(challenge_name)
        compose = self._compose_files.get(challenge_name)
        if not project:
            return
        # Reuse the exact compose file and unique project name used at startup.
        proc = await asyncio.create_subprocess_exec(
            "docker", "compose", "-f", str(compose), "-p", project, "down", "--remove-orphans",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        if proc.returncode != 0:
            raise RuntimeError((stderr or stdout).decode("utf-8", errors="replace")[-4000:])
        self._projects.pop(challenge_name, None)
        self._compose_files.pop(challenge_name, None)

    async def stop_all(self) -> None:
        for challenge_name in list(self._projects):
            try:
                await self.stop(challenge_name)
            except Exception as exc:
                logger.warning("Could not stop environment %s: %s", challenge_name, exc)
