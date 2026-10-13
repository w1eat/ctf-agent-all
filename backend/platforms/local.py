"""Adapter for already-downloaded challenge directories."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from backend.platforms.environments import LocalEnvironmentManager
from backend.platforms.models import (
    ChallengeBundle,
    EnvironmentInfo,
    PlatformProfile,
    SubmissionResult,
)
from backend.platforms.state import AttachmentArtifact, AttachmentCandidate, ChallengeStateStore


def re_slug(name: str) -> str:
    slug = re.sub(r'[<>:"/\\|?*\.\x00-\x1f]', "", name.lower().strip())
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-") or "challenge"


class LocalPlatformAdapter:
    browser_submission = False

    def __init__(self, challenges_root: str = "challenges", *, settings=None, allow_submit: bool = False) -> None:
        self.root = Path(challenges_root)
        self.allow_submit = allow_submit
        self._bundles: dict[str, ChallengeBundle] = {}
        self._directories: dict[str, Path] = {}
        self._environments: dict[str, EnvironmentInfo] = {}
        self._environment_manager = LocalEnvironmentManager(self.root)
        self.state = ChallengeStateStore(
            getattr(settings, "challenge_state_db_path", str(self.root / ".challenge_state.sqlite3")),
            run_id=getattr(settings, "challenge_run_id", "") or None,
        )

    async def start(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    async def discover(self) -> PlatformProfile:
        return PlatformProfile(
            name="local",
            origin=str(self.root.resolve()),
            authenticated=True,
            capabilities={"list", "download", "local_environment"},
        )

    def _load_bundle(self, directory: Path) -> ChallengeBundle | None:
        metadata = directory / "metadata.yml"
        if not metadata.exists():
            return None
        data = yaml.safe_load(metadata.read_text(encoding="utf-8")) or {}
        bundle = ChallengeBundle.from_metadata(data)
        files = sorted(
            path.relative_to(directory).as_posix()
            for path in (directory / "distfiles").rglob("*")
            if path.is_file() and not path.is_symlink()
        ) if (directory / "distfiles").exists() else []
        return bundle.model_copy(update={"files": files}).normalized()

    async def list_challenges(self) -> list[ChallengeBundle]:
        bundles = []
        for directory in sorted(self.root.iterdir() if self.root.exists() else []):
            if not directory.is_dir():
                continue
            bundle = self._load_bundle(directory)
            if bundle:
                bundles.append(bundle)
        names = [bundle.name for bundle in bundles]
        if len(names) != len(set(names)):
            duplicates = sorted({name for name in names if names.count(name) > 1})
            raise ValueError(f"Duplicate challenge names are unsupported: {duplicates}")
        native_ids = [bundle.native_id for bundle in bundles]
        if len(native_ids) != len(set(native_ids)):
            duplicates = sorted({native_id for native_id in native_ids if native_ids.count(native_id) > 1})
            raise ValueError(f"Duplicate challenge native IDs are unsupported: {duplicates}")
        self._bundles = {bundle.name: bundle for bundle in bundles}
        self._directories = {
            bundle.name: directory
            for directory in (self.root.iterdir() if self.root.exists() else [])
            if directory.is_dir() and (bundle := self._load_bundle(directory)) is not None
        }
        for index, bundle in enumerate(bundles):
            directory = self._directories[bundle.name]
            running_environment = self._environments.get(bundle.name)
            if running_environment:
                environment = {**bundle.environment, **running_environment.model_dump(exclude_none=True)}
                bundle = bundle.model_copy(update={
                    "connection_info": bundle.connection_info or running_environment.url,
                    "environment": environment,
                }).normalized()
                bundles[index] = bundle
                self._bundles[bundle.name] = bundle
            environment_required = bool(
                bundle.environment_required
                or bundle.connection_info
                or bundle.environment
            )
            is_compose = bundle.environment.get("source") in ("compose", "docker-compose")
            if running_environment:
                environment_ready = running_environment.status == "ready"
            elif is_compose:
                environment_ready = False
            else:
                environment_ready = bool(
                    bundle.connection_info
                    or bundle.environment.get("url")
                    or (bundle.environment.get("host") and bundle.environment.get("port"))
                    or bundle.environment.get("status") == "ready"
                )
            if environment_required and not environment_ready:
                state = "waiting_for_environment"
            elif bundle.files or environment_ready:
                state = "ready"
            else:
                state = "needs_input"
            if state == "waiting_for_environment":
                reason = (
                    "local Compose environment has not been started"
                    if is_compose else "environment required but not registered"
                )
            elif state == "needs_input":
                reason = "missing attachment or environment"
            else:
                reason = ""
            previous = self.state.get_challenge(bundle.native_id)
            if previous and previous["state"] in {"needs_input", "failed", "running", "solved"}:
                state = previous["state"]
                reason = previous["reason"]
            self.state.upsert_challenge(
                native_id=bundle.native_id,
                name=bundle.name,
                slug=re_slug(bundle.name),
                platform=bundle.platform,
                mode=bundle.mode.value,
                package_dir=str(directory),
                connection_info=bundle.connection_info,
                environment=bundle.environment,
                state=state,
                reason=reason,
            )
        return bundles

    async def prepare_challenge(self, challenge_id: str) -> ChallengeBundle:
        bundles = await self.list_challenges()
        bundle = next(
            (item for item in bundles if item.name == challenge_id or item.native_id == str(challenge_id)),
            None,
        )
        if bundle is None:
            raise RuntimeError(f"Local challenge {challenge_id!r} not found")
        return bundle

    async def start_environment(self, challenge_id: str) -> EnvironmentInfo:
        bundle = await self.prepare_challenge(challenge_id)
        existing = self._environments.get(bundle.name)
        if existing:
            return existing
        env = bundle.environment
        if env.get("source") in ("compose", "docker-compose"):
            challenge_dir = self._directories.get(bundle.name, self.root / re_slug(bundle.name))
            env = {**env, "challenge_dir": str(challenge_dir.relative_to(self.root))}
            info = await self._environment_manager.start(bundle.name, env)
            self._environments[bundle.name] = info
            await self.list_challenges()
            return info
        if bundle.connection_info:
            return EnvironmentInfo(status="ready", source="remote", url=bundle.connection_info)
        raise RuntimeError(f"Challenge {bundle.name!r} has no local environment or connection_info")

    async def get_solve_status(self) -> set[str]:
        status_path = self.root / ".solve-status.json"
        if not status_path.exists():
            return set()
        try:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("solved", []), list):
                raise ValueError("solve status must contain a solved list")
            return set(data.get("solved", []))
        except (OSError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Could not read local solve status from {status_path}") from exc

    async def list_attachment_candidates(self, challenge_id: str) -> list[AttachmentCandidate]:
        bundle = await self.prepare_challenge(challenge_id)
        candidates = []
        for relative in bundle.files:
            name = Path(relative).name
            candidate = AttachmentCandidate(attachment_id=relative, name=name, metadata={"relative_path": relative})
            self.state.upsert_attachment(bundle.native_id, candidate, state="ready")
            candidates.append(candidate)
        return candidates

    async def download_attachment(self, challenge_id: str, attachment_id: str) -> AttachmentArtifact:
        bundle = await self.prepare_challenge(challenge_id)
        directory = self._directories[bundle.name]
        path = (directory / attachment_id).resolve()
        if directory.resolve() not in path.parents or not path.is_file():
            raise FileNotFoundError(f"Local attachment not found: {attachment_id}")
        digest, size = self.state.sha256_file(path)
        relative = path.relative_to(directory).as_posix()
        self.state.set_attachment_state(bundle.native_id, attachment_id, "ready", relative_path=relative, sha256=digest, byte_count=size)
        return AttachmentArtifact(attachment_id, path.name, relative, digest, size)

    async def get_challenge_state(self, challenge_id: str) -> dict:
        bundle = await self.prepare_challenge(challenge_id)
        state = self.state.get_challenge(bundle.native_id) or {}
        state["attachments"] = self.state.list_attachments(bundle.native_id)
        return state

    async def mark_needs_input(self, challenge_id: str, reason: str) -> str:
        bundle = await self.prepare_challenge(challenge_id)
        self.state.set_challenge_state(bundle.native_id, "needs_input", reason)
        return f"{challenge_id}: needs_input — {reason}"

    async def retry_challenge_preparation(self, challenge_id: str) -> str:
        bundle = await self.prepare_challenge(challenge_id)
        self.state.retry_challenge(bundle.native_id)
        return f"{challenge_id}: preparation reset"

    async def submit_flag(self, challenge_id: str, flag: str) -> SubmissionResult:
        raise RuntimeError(
            "Local platform cannot submit flags. Use --platform auto so Playwright MCP "
            "performs and verifies the submission."
        )

    async def confirm_submission(
        self, challenge_id: str, flag: str, accepted: bool, reason: str
    ) -> SubmissionResult:
        raise RuntimeError("Local platform cannot confirm browser submissions")

    async def close(self) -> None:
        await self._environment_manager.stop_all()
        self._environments.clear()
        self.state.close_run()
