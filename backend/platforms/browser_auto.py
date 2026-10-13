"""Public browser-first platform entry point."""

from backend.platforms.browser_mcp import (
    ALLOWED_BROWSER_TOOLS,
    BROWSER_TOOL_SCHEMAS,
    BrowserAutoPlatformAdapter,
    BrowserMCPClient,
)

__all__ = [
    "ALLOWED_BROWSER_TOOLS",
    "BROWSER_TOOL_SCHEMAS",
    "BrowserAutoPlatformAdapter",
    "BrowserMCPClient",
]
