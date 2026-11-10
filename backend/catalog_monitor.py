"""Platform-neutral catalog discovery schema and refresh scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CATALOG_DISCOVERY_TOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "challenges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "native_id": {"type": ["string", "integer"]},
                    "challenge_id": {"type": ["string", "integer"]},
                    "name": {"type": "string"},
                    "challenge_url": {"type": "string"},
                    "category": {"type": "string"},
                    "points": {"type": "integer"},
                    "description": {"type": "string"},
                    "locked": {"type": ["boolean", "null"]},
                    "solved": {"type": ["boolean", "null"]},
                },
                "required": ["name"],
                "anyOf": [{"required": ["native_id"]}, {"required": ["challenge_id"]}],
            },
        },
        "sources": {
            "type": "array",
            "description": "Observed credential-free listing pages or read-only API URLs; never include headers or tokens.",
            "items": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "kind": {"type": "string", "enum": ["page", "api"]},
                    "navigation": {"type": "string", "description": "Short observed navigation or pagination instructions."},
                    "active": {"type": "boolean", "description": "Set false only after confirming this exact source is obsolete."},
                },
                "required": ["url", "kind"],
            },
        },
        "scan_complete": {
            "type": "boolean",
            "description": "True only after all known sources and pages were successfully observed in this scan.",
        },
    },
    "required": ["challenges"],
}


@dataclass
class CatalogRefreshSchedule:
    interval_seconds: float
    started_at: float
    debounce_seconds: float = 2.0
    retry_seconds: float = 30.0
    _next_periodic: float | None = field(init=False)
    _pending_at: float | None = field(default=None, init=False)
    _reasons: set[str] = field(default_factory=set, init=False)
    _failures: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._next_periodic = (
            self.started_at + self.interval_seconds if self.interval_seconds > 0 else None
        )

    def request(self, reason: str, now: float) -> None:
        self._reasons.add(reason)
        requested_at = now + self.debounce_seconds
        self._pending_at = min(self._pending_at, requested_at) if self._pending_at is not None else requested_at

    def retry(self, now: float) -> None:
        self._reasons.add("previous refresh was incomplete")
        self._failures += 1
        retry_at = now + min(self.retry_seconds * (2 ** min(self._failures - 1, 4)), 300)
        self._pending_at = min(self._pending_at, retry_at) if self._pending_at is not None else retry_at

    def succeeded(self, now: float | None = None) -> None:
        self._failures = 0
        self._reasons.clear()
        self._pending_at = None
        if now is not None:
            self._next_periodic = now + self.interval_seconds if self.interval_seconds > 0 else None

    def wait_seconds(self, now: float, maximum: float = 5.0) -> float:
        deadlines = [deadline for deadline in (self._next_periodic, self._pending_at) if deadline is not None]
        return min(maximum, max(0.0, min(deadlines) - now)) if deadlines else maximum

    def take_due(self, now: float) -> list[str]:
        periodic = self._next_periodic is not None and now >= self._next_periodic
        requested = self._pending_at is not None and now >= self._pending_at
        if not periodic and not requested:
            return []
        reasons = sorted(self._reasons)
        if periodic:
            reasons.append("periodic refresh")
        self._reasons.clear()
        self._pending_at = None
        self._next_periodic = now + self.interval_seconds if self.interval_seconds > 0 else None
        return reasons
