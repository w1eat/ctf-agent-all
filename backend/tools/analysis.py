"""Model-facing wrappers for the shared reverse-engineering MCP gateway."""

from __future__ import annotations

import json
from typing import Any

from pydantic_ai import RunContext

from backend.deps import SolverDeps


async def list_analysis_tools(ctx: RunContext[SolverDeps]) -> str:
    """List MCP tools ready for this challenge, including eligible file IDs."""
    gateway = ctx.deps.analysis_gateway
    if not gateway:
        return "Solver MCP is not enabled for this run."
    result = await gateway.list_analysis_tools(ctx.deps.challenge_name)
    return json.dumps(result, ensure_ascii=False, default=str)


async def call_analysis_tool(
    ctx: RunContext[SolverDeps],
    server: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    file_id: str = "",
) -> str:
    """Call a discovered IDA, JADX, or Kali MCP tool for this challenge."""
    gateway = ctx.deps.analysis_gateway
    if not gateway:
        return "Solver MCP is not enabled for this run."
    result = await gateway.call_analysis_tool(
        ctx.deps.challenge_name, server, tool_name, arguments or {}, file_id
    )
    return json.dumps(result, ensure_ascii=False, default=str)


async def analysis_status(ctx: RunContext[SolverDeps]) -> str:
    """Show MCP connection and per-file analysis readiness for this challenge."""
    gateway = ctx.deps.analysis_gateway
    if not gateway:
        return "Solver MCP is not enabled for this run."
    return json.dumps(
        gateway.analysis_status(ctx.deps.challenge_name), ensure_ascii=False, default=str
    )
