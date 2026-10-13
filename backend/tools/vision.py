"""Vision tool — native multimodal BinaryContent."""

from pydantic_ai import BinaryContent, RunContext

from backend.deps import SolverDeps
from backend.tools.core import do_view_image


async def view_image(
    ctx: RunContext[SolverDeps],
    filename: str,
) -> str | BinaryContent:
    """Visually inspect an image — use this IMMEDIATELY on any image challenge.

    Searches /challenge/distfiles/ first, then /challenge/workspace/.
    Returns an error if the image cannot be loaded (fix magic bytes first if corrupt).
    filename: Filename to view, e.g. 'flag.png' or 'fixed.jpg'.
    """
    result = await do_view_image(ctx.deps.sandbox, filename, ctx.deps.use_vision)
    if isinstance(result, tuple):
        data, media_type = result
        return BinaryContent(data=data, media_type=media_type)
    return result
