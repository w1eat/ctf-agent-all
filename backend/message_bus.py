"""Per-challenge message bus for inter-agent communication."""

from __future__ import annotations

import asyncio
import itertools
import time
from dataclasses import dataclass, field


@dataclass
class Finding:
    model: str
    content: str
    timestamp: float = field(default_factory=time.time)
    event_type: str = "finding"
    role: str = ""
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()
    event_id: int = 0


MAX_FINDINGS = 200


@dataclass
class ChallengeMessageBus:
    """Append-only shared findings list with per-model cursors."""

    findings: list[Finding] = field(default_factory=list)
    cursors: dict[str, int] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _event_ids: itertools.count = field(default_factory=lambda: itertools.count(1), repr=False)

    async def post(
        self,
        model: str,
        content: str,
        *,
        event_type: str = "finding",
        role: str = "",
        confidence: float = 0.0,
        evidence: tuple[str, ...] = (),
    ) -> None:
        """Post a finding from a solver."""
        async with self._lock:
            self.findings.append(
                Finding(
                    model=model,
                    content=str(content)[:4000],
                    event_type=event_type,
                    role=role,
                    confidence=max(0.0, min(1.0, float(confidence))),
                    evidence=tuple(str(item)[:1000] for item in evidence[:20]),
                    event_id=next(self._event_ids),
                )
            )
            if len(self.findings) > MAX_FINDINGS:
                trim = len(self.findings) - MAX_FINDINGS
                self.findings = self.findings[trim:]
                self.cursors = {k: max(0, v - trim) for k, v in self.cursors.items()}

    async def check(self, model: str) -> list[Finding]:
        """Get unread findings from other models. Advances the cursor."""
        async with self._lock:
            cursor = self.cursors.get(model, 0)
            unread = [f for f in self.findings[cursor:] if f.model != model]
            self.cursors[model] = len(self.findings)
            return unread

    async def broadcast(self, content: str, source: str = "coordinator") -> None:
        """Coordinator broadcasts a message to all solvers."""
        await self.post(source, content)

    async def post_event(
        self,
        model: str,
        event_type: str,
        summary: str,
        *,
        role: str = "",
        confidence: float = 0.0,
        evidence: tuple[str, ...] = (),
    ) -> None:
        """Publish a structured event while retaining the legacy API."""
        await self.post(
            model,
            summary,
            event_type=event_type,
            role=role,
            confidence=confidence,
            evidence=evidence,
        )

    def format_unread(self, findings: list[Finding]) -> str:
        """Format findings for injection into a solver prompt."""
        if not findings:
            return ""
        parts = [
            f"[{f.model}/{f.event_type}] {f.content}"
            + (f" Evidence: {'; '.join(f.evidence[:3])}" if f.evidence else "")
            for f in findings
        ]
        return "**Findings from other agents:**\n\n" + "\n\n".join(parts)
