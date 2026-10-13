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
    """Block every spawn until the Coordinator's setup turn has returned."""
    issue = submission_recipe_issue(deps)
    if issue:
        return issue
    if (not deps.no_submit and getattr(deps.platform, "browser_submission", False)
            and not deps.submission_setup_complete):
        return "Coordinator submission setup phase is still in progress"
    return None


async def ensure_submission_setup(
    deps: CoordinatorDeps,
    turn_fn: Callable[[str], Awaitable[Any]],
    *,
    max_turns: int = 3,
) -> str | None:
    """Ask the already-running Coordinator to prepare submission before solving.

    No candidate Flag is provided and the setup turn must not submit a test
    value. The readiness result is checked by code, not the model's assertion.
    """
    issue = submission_recipe_issue(deps)
    if issue is None:
        deps.submission_setup_complete = True
        return None
    platform = deps.platform
    origin = getattr(platform, "base_url", "")
    known = await platform.list_challenges()
    pages = [
        f"{item.name}: {item.challenge_url} (id={item.native_id})"
        for item in known if getattr(item, "challenge_url", "")
    ][:5]
    context = "\n".join(pages) if pages else "No challenge page has been registered yet; browse the platform to find one."
    for attempt in range(1, max_turns + 1):
        message = (
            "MANDATORY SUBMISSION SETUP PHASE before solving. "
            f"Configured origin: {origin}. Current readiness error: {issue}.\n"
            f"Known challenge pages:\n{context}\n"
            "Use the authenticated browser tools (snapshot before interaction) to inspect "
            "an unsolved challenge's flag input and observed submit interaction. If the "
            "currently selected challenge is already solved and its input is disabled, "
            "choose an unsolved challenge instead. Save a reusable "
            "credential-free recipe with save_recipe: platform_origin must be the "
            "configured origin; steps must navigate to a same-origin challenge URL "
            "templated with {challenge_id}, input {flag} using a visible target. "
            "Each step's target must be a plain string containing a stable unique "
            "CSS selector observed from the page (for example, "
            "textarea[aria-label=\"Flag\"]); do not pass a role/name object or a "
            "snapshot-only ref such as e134, because refs change between pages. "
            "For submission, either click an observed submit button or set "
            "data.submit=true on the {flag} type step when the page explicitly submits on Enter. "
            "Use the exact step fields: "
            "{\"action\":\"navigate\",\"value\":\"https://host/challenges/{challenge_id}\"}, "
            "then {\"action\":\"type\",\"target\":\"textarea[aria-label=\\\"Flag\\\"]\","
            "\"value\":\"{flag}\",\"data\":{\"submit\":true}}. "
            "Replace host/path with the observed same-origin challenge URL. Include "
            "observed success/failure text only as hints. Do NOT enter any flag or "
            "trigger the submit interaction during setup. "
            "Do NOT spawn swarms, submit flags, or claim confirmation in this phase. "
            "If login or UI inspection is blocked, describe the blocker. "
            f"Setup attempt {attempt}/{max_turns}."
        )
        logger.info("Coordinator submission setup attempt %s/%s: %s", attempt, max_turns, issue)
        try:
            await turn_fn(message)
        except CoordinatorTurnError as exc:
            logger.error("Coordinator submission setup stopped: %s", exc)
            return str(exc)
        issue = submission_recipe_issue(deps)
        if issue is None:
            deps.submission_setup_complete = True
            logger.info("Coordinator submission recipe is ready for %s", origin)
            return None
    return issue
