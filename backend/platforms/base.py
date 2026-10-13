"""Platform adapter protocol and common lifecycle errors."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Protocol, runtime_checkable

from backend.platforms.models import (
    ChallengeBundle,
    EnvironmentInfo,
    PlatformProfile,
    SubmissionResult,
)
from backend.platforms.state import AttachmentArtifact, AttachmentCandidate


class PlatformAdapter(Protocol):
    """Operations required by the coordinator, independent of platform brand."""

    async def start(self) -> None: ...

    async def discover(self) -> PlatformProfile: ...

    async def list_challenges(self) -> list[ChallengeBundle]: ...

    async def prepare_challenge(self, challenge_id: str) -> ChallengeBundle: ...

    async def list_attachment_candidates(self, challenge_id: str) -> list[AttachmentCandidate]: ...

    async def download_attachment(self, challenge_id: str, attachment_id: str) -> AttachmentArtifact: ...

    async def get_challenge_state(self, challenge_id: str) -> dict: ...

    async def mark_needs_input(self, challenge_id: str, reason: str) -> str: ...

    async def retry_challenge_preparation(self, challenge_id: str) -> str: ...

    async def start_environment(self, challenge_id: str) -> EnvironmentInfo: ...

    async def get_solve_status(self) -> set[str]: ...

    async def submit_flag(self, challenge_id: str, flag: str) -> SubmissionResult: ...

    async def confirm_submission(
        self, challenge_id: str, flag: str, accepted: bool, reason: str
    ) -> SubmissionResult: ...

    async def close(self) -> None: ...


@runtime_checkable
class BrowserToolProvider(Protocol):
    async def call_browser_tool(self, name: str, arguments: dict) -> str: ...

    def browser_tool_specs(self) -> list[dict]: ...


SubmitCallback = Awaitable[tuple[str, bool]]
