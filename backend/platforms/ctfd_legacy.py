"""Compatibility adapter for the original standard CTFd integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from backend.ctfd import CTFdClient
from backend.platforms.local import re_slug
from backend.platforms.models import (
    ChallengeBundle,
    EnvironmentInfo,
    PlatformProfile,
    SubmissionResult,
)
from backend.platforms.state import AttachmentArtifact, AttachmentCandidate, ChallengeStateStore


class CTFdLegacyAdapter:
    """Translate the existing CTFd client into the platform-neutral contract."""

    browser_submission = False

    def __init__(self, client: CTFdClient, challenges_root: str = "challenges", *, settings=None) -> None:
        self.client = client
        self.challenges_root = challenges_root
        self._bundles: dict[str, ChallengeBundle] = {}
        self.state = ChallengeStateStore(
            getattr(settings, "challenge_state_db_path", ".runtime/challenge_state.sqlite3"),
            run_id=getattr(settings, "challenge_run_id", "") or None,
        )

    async def start(self) -> None:
        return None

    async def discover(self) -> PlatformProfile:
        return PlatformProfile(
            name="ctfd",
            origin=self.client.base_url.rstrip("/"),
            authenticated=bool(self.client.token or self.client._logged_in),
            capabilities={"list", "download", "solve_status"},
            evidence=["standard CTFd REST API adapter"],
        )

    @staticmethod
    def _bundle(raw: dict[str, Any]) -> ChallengeBundle:
        files = raw.get("files") or []
        return ChallengeBundle(
            platform="ctfd",
            native_id=str(raw.get("id", raw.get("name", ""))),
            name=raw.get("name", "Unknown"),
            category=raw.get("category", ""),
            points=int(raw.get("value", 0) or 0),
            description=raw.get("description", "") or "",
            files=files,
            connection_info=raw.get("connection_info", "") or "",
            environment={},
            capabilities={"download"} if files else set(),
            source_data=raw,
        ).normalized()

    async def list_challenges(self) -> list[ChallengeBundle]:
        raw = await self.client.fetch_all_challenges()
        bundles = [self._bundle(item) for item in raw]
        names = [bundle.name for bundle in bundles]
        if len(names) != len(set(names)):
            duplicates = sorted({name for name in names if names.count(name) > 1})
            raise ValueError(f"Duplicate challenge names are unsupported: {duplicates}")
        slugs = [re_slug(name) for name in names]
        if len(slugs) != len(set(slugs)):
            raise ValueError("Challenge names collide after directory normalization")
        self._bundles = {bundle.name: bundle for bundle in bundles}
        return bundles

    async def prepare_challenge(self, challenge_id: str) -> ChallengeBundle:
        bundles = await self.list_challenges()
        bundle = next(
            (item for item in bundles if item.native_id == str(challenge_id) or item.name == challenge_id),
            None,
        )
        if bundle is None:
            raise RuntimeError(f"Challenge {challenge_id!r} not found in CTFd")
        raw = bundle.source_data
        try:
            challenge_dir = await self.client.pull_challenge(raw, self.challenges_root)
        except Exception as exc:
            self.state.upsert_challenge(
                native_id=bundle.native_id,
                name=bundle.name,
                slug=re_slug(bundle.name),
                platform=bundle.platform,
                mode=bundle.mode.value,
                package_dir=str(Path(self.challenges_root) / re_slug(bundle.name)),
                state="needs_input",
                reason=str(exc),
            )
            raise
        metadata_path = Path(challenge_dir) / "metadata.yml"
        pulled_metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
        declared_files = (pulled_metadata or {}).get("files")
        files = (
            [str(item) for item in declared_files]
            if declared_files is not None
            else [path.relative_to(challenge_dir).as_posix() for path in Path(challenge_dir).glob("distfiles/*") if path.is_file()]
        )
        if any(not (Path(challenge_dir) / path).is_file() for path in files):
            raise RuntimeError(f"CTFd challenge {bundle.name!r} has missing downloaded attachments")
        bundle = bundle.model_copy(update={"files": files})
        (Path(challenge_dir) / "metadata.yml").write_text(
            yaml.safe_dump(bundle.metadata_dict(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self._bundles[bundle.name] = bundle
        self.state.upsert_challenge(
            native_id=bundle.native_id,
            name=bundle.name,
            slug=Path(challenge_dir).name,
            platform=bundle.platform,
            mode=bundle.mode.value,
            package_dir=challenge_dir,
            connection_info=bundle.connection_info,
            environment=bundle.environment,
            state="ready" if files or bundle.connection_info else "needs_input",
            reason="missing attachment or environment" if not files and not bundle.connection_info else "",
        )
        return bundle

    async def list_attachment_candidates(self, challenge_id: str) -> list[AttachmentCandidate]:
        bundle = await self.prepare_challenge(challenge_id)
        candidates = []
        for relative in bundle.files:
            candidate = AttachmentCandidate(relative, Path(relative).name, metadata={"relative_path": relative})
            self.state.upsert_attachment(bundle.native_id, candidate, state="ready")
            candidates.append(candidate)
        return candidates

    async def download_attachment(self, challenge_id: str, attachment_id: str) -> AttachmentArtifact:
        bundle = await self.prepare_challenge(challenge_id)
        directory = Path(self.challenges_root) / re_slug(bundle.name)
        path = (directory / attachment_id).resolve()
        if directory.resolve() not in path.parents or not path.is_file():
            raise FileNotFoundError(f"CTFd attachment not found: {attachment_id}")
        digest, size = self.state.sha256_file(path)
        relative = path.relative_to(directory).as_posix()
        self.state.set_attachment_state(bundle.native_id, attachment_id, "ready", relative_path=relative, sha256=digest, byte_count=size)
        return AttachmentArtifact(attachment_id, path.name, relative, digest, size)

    async def get_challenge_state(self, challenge_id: str) -> dict:
        bundle = await self._state_bundle(challenge_id)
        state = self.state.get_challenge(bundle.native_id) or {}
        state["attachments"] = self.state.list_attachments(bundle.native_id)
        return state

    async def mark_needs_input(self, challenge_id: str, reason: str) -> str:
        bundle = await self._state_bundle(challenge_id)
        self.state.set_challenge_state(bundle.native_id, "needs_input", reason)
        return f"{challenge_id}: needs_input — {reason}"

    async def retry_challenge_preparation(self, challenge_id: str) -> str:
        bundle = await self._state_bundle(challenge_id)
        self.state.retry_challenge(bundle.native_id)
        return f"{challenge_id}: preparation reset"

    async def _state_bundle(self, challenge_id: str) -> ChallengeBundle:
        bundle = next(
            (item for item in self._bundles.values()
             if item.name == challenge_id or item.native_id == str(challenge_id)),
            None,
        )
        if bundle and self.state.get_challenge(bundle.native_id):
            return bundle
        return await self.prepare_challenge(challenge_id)

    async def start_environment(self, challenge_id: str) -> EnvironmentInfo:
        bundle = self._bundles.get(challenge_id)
        if bundle and bundle.connection_info:
            return EnvironmentInfo(status="ready", source="remote", url=bundle.connection_info)
        raise RuntimeError("CTFd challenge has no connection_info; start the target on the platform first")

    async def get_solve_status(self) -> set[str]:
        return await self.client.fetch_solved_names()

    async def submit_flag(self, challenge_id: str, flag: str) -> SubmissionResult:
        raise RuntimeError(
            "Direct CTFd API submission has been removed. Use --platform auto so "
            "Playwright MCP performs and verifies the submission."
        )

    async def confirm_submission(
        self, challenge_id: str, flag: str, accepted: bool, reason: str
    ) -> SubmissionResult:
        raise RuntimeError("CTFd API mode cannot confirm browser submissions")

    async def close(self) -> None:
        self.state.close_run()
        await self.client.close()
