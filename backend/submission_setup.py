"""Submission readiness gate shared by Coordinator turns and swarm spawning."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend.deps import CoordinatorDeps

logger = logging.getLogger(__name__)


class CoordinatorTurnError(RuntimeError):
    """The coordinator could not complete a setup turn."""


def submission_recipe_issue(deps: CoordinatorDeps) -> str | None:
    """Check the recipe without treating an unfinished setup turn as complete."""
    if deps.no_submit or not getattr(deps.platform, "browser_submission", False):
        return None
    check = getattr(deps.platform, "submission_recipe_issue", None)
    if not callable(check):
        return "Browser platform cannot check submission recipe readiness"
    return check()


def submission_setup_issue(deps: CoordinatorDeps) -> str | None:
    """Global setup no longer implies a submission contract for every challenge."""
    return None


async def ensure_submission_setup(
    deps: CoordinatorDeps,
    turn_fn: Callable[[str], Awaitable[Any]],
    *,
    max_turns: int = 3,
) -> str | None:
    """Initialize coordination; submission discovery happens per challenge."""
    # Submission contracts are discovered per challenge during coordination.
    # A single platform-wide recipe cannot establish readiness for all types.
    deps.submission_setup_complete = True
    return None
