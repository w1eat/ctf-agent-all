"""Flag submission tool."""

from pydantic_ai import RunContext

from backend.deps import SolverDeps
from backend.tools.core import do_confirm_submission, do_submit_flag


async def submit_flag(ctx: RunContext[SolverDeps], flag: str) -> str:
    """Submit a flag through the configured platform to verify it.

    Returns CORRECT, ALREADY SOLVED, or INCORRECT.
    Do NOT submit placeholder flags like CTF{flag} or CTF{placeholder}.
    """
    if ctx.deps.no_submit:
        return f'DRY RUN — would submit "{flag.strip()}" but --no-submit is set.'

    # Use deduped submission via swarm if available, otherwise direct platform call.
    if ctx.deps.submit_fn:
        display, is_confirmed = await ctx.deps.submit_fn(flag)
    else:
        display, is_confirmed = await do_submit_flag(ctx.deps.platform, ctx.deps.challenge_name, flag)
    if is_confirmed:
        ctx.deps.confirmed_flag = flag.strip()
    return display


async def confirm_submission(ctx: RunContext[SolverDeps], flag: str, accepted: bool, reason: str) -> str:
    """Confirm or reject a browser submission using the visible page evidence."""
    if ctx.deps.no_submit:
        return "DRY RUN — submission confirmation is disabled because --no-submit is set."
    display, is_confirmed = await do_confirm_submission(
        ctx.deps.platform, ctx.deps.challenge_name, flag, accepted, reason
    )
    if is_confirmed:
        ctx.deps.confirmed_flag = flag.strip()
    return display
