"""Platform integrations for challenge discovery, environments, and submission."""

from backend.platforms.base import PlatformAdapter
from backend.platforms.models import (
    ChallengeBundle,
    ChallengeMode,
    ChallengeState,
    EnvironmentInfo,
    PlatformProfile,
    SubmissionResult,
)
from backend.platforms.state import AttachmentArtifact, AttachmentCandidate, ChallengeStateStore

__all__ = [
    "ChallengeBundle",
    "ChallengeMode",
    "ChallengeState",
    "EnvironmentInfo",
    "PlatformAdapter",
    "PlatformProfile",
    "SubmissionResult",
    "AttachmentArtifact",
    "AttachmentCandidate",
    "ChallengeStateStore",
]
