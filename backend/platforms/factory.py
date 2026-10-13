"""Construct the configured platform implementation."""

from __future__ import annotations

from typing import Any

from backend.ctfd import CTFdClient
from backend.platforms.base import PlatformAdapter
from backend.platforms.browser_auto import BrowserAutoPlatformAdapter
from backend.platforms.ctfd_legacy import CTFdLegacyAdapter
from backend.platforms.local import LocalPlatformAdapter


def create_platform(settings: Any, challenges_root: str, *, allow_submit: bool = False) -> PlatformAdapter:
    platform = str(getattr(settings, "platform", "auto")).lower()
    if allow_submit and platform != "auto":
        raise ValueError(
            "Flag submission is Playwright MCP-only. Use --platform auto with --submit."
        )
    if platform == "local":
        return LocalPlatformAdapter(challenges_root, settings=settings, allow_submit=False)
    if platform == "ctfd":
        client = CTFdClient(
            base_url=settings.ctfd_url,
            token=settings.ctfd_token,
            username=settings.ctfd_user,
            password=settings.ctfd_pass,
        )
        return CTFdLegacyAdapter(client, challenges_root, settings=settings)
    if platform == "auto":
        return BrowserAutoPlatformAdapter(settings, challenges_root, allow_submit=allow_submit)
    raise ValueError(f"Unknown platform: {platform}. Use auto, ctfd, or local.")
