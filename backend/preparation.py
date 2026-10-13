"""Program-level challenge package preparation queue."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from backend.platforms.models import ChallengeState

logger = logging.getLogger(__name__)

PREPARABLE_STATES = {
    ChallengeState.WAITING_FOR_DECISION.value,
    ChallengeState.PREPARING.value,
    ChallengeState.WAITING_FOR_PACKAGE.value,
}


@dataclass(frozen=True)
class PreparationEvent:
    challenge_name: str
    state: str
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class ChallengePreparationManager:
    """Continuously prepares registered browser-platform challenges."""

    def __init__(self, platform: Any, *, concurrency: int = 4, scan_interval: float = 1.0) -> None:
        self.platform = platform
        self.concurrency = max(1, concurrency)
        self.scan_interval = scan_interval
        self.events: asyncio.Queue[PreparationEvent] = asyncio.Queue()
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._scheduled: set[str] = set()
        self._active: set[str] = set()
        self._workers: list[asyncio.Task[None]] = []
        self._scanner: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._resume = asyncio.Event()
        self._resume.set()

    @property
    def supported(self) -> bool:
        return callable(getattr(self.platform, "prepare_challenge_package", None))

    @property
    def active_count(self) -> int:
        return len(self._active)

    @property
    def queued_count(self) -> int:
        return self._queue.qsize()

    async def start(self) -> None:
        if not self.supported or self._workers:
            return
        await self.scan_once()
        self._workers = [
            asyncio.create_task(self._worker(index), name=f"challenge-preparer-{index}")
            for index in range(self.concurrency)
        ]
        self._scanner = asyncio.create_task(self._scan_loop(), name="challenge-preparation-scan")

    async def stop(self) -> None:
        self._stop.set()
        self._resume.set()
        tasks = [*self._workers]
        if self._scanner:
            tasks.append(self._scanner)
        for task in tasks:
            task.cancel()
        if tasks:
            # asyncio.wait never re-raises a child's cancellation, unlike gather, which
            # propagates it even with return_exceptions=True once its own future is
            # cancelled - that re-raised a child's CancelledError during coordinator
            # shutdown and aborted the remaining cleanup steps.
            await asyncio.wait(tasks)
            for task in tasks:
                if task.cancelled():
                    continue
                if (exc := task.exception()) is not None:
                    logger.warning("Preparation task %s failed during shutdown: %s",
                                   task.get_name(), exc)
        self._workers.clear()
        self._scanner = None

    async def enqueue(self, challenge_name: str) -> bool:
        if not self.supported or challenge_name in self._scheduled:
            return False
        self._scheduled.add(challenge_name)
        self._queue.put_nowait(challenge_name)
        return True

    async def scan_once(self) -> None:
        if not self.supported:
            return
        try:
            challenges = await self.platform.list_challenges()
        except Exception as exc:
            logger.warning("Preparation scan failed: %s", exc)
            return
        for challenge in challenges:
            state = challenge.state.value if hasattr(challenge.state, "value") else str(challenge.state)
            attachment_scan_pending = (
                state == ChallengeState.READY.value
                and not challenge.files
                and not challenge.source_data.get("attachments_scanned")
            )
            if state in PREPARABLE_STATES or attachment_scan_pending:
                await self.enqueue(challenge.name)

    async def _scan_loop(self) -> None:
        while not self._stop.is_set():
            await asyncio.sleep(self.scan_interval)
            await self.scan_once()

    async def _worker(self, index: int) -> None:
        prepare = self.platform.prepare_challenge_package
        while not self._stop.is_set():
            name = await self._queue.get()
            await self._resume.wait()
            self._active.add(name)
            try:
                outcome = await prepare(name)
                state = str(outcome.get("state", "needs_input"))
                message = str(outcome.get("message", ""))
                details = dict(outcome.get("details") or {})
                self.events.put_nowait(PreparationEvent(name, state, message, details))
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Preparation failed for %s: %s", name, exc, exc_info=True)
                self.events.put_nowait(
                    PreparationEvent(name, "needs_input", str(exc), {"error": str(exc)})
                )
            finally:
                self._active.discard(name)
                self._scheduled.discard(name)
                self._queue.task_done()

    async def pause_and_wait(self) -> None:
        """Keep coordinator browser turns from interleaving with preparation workflows."""
        self._resume.clear()
        while self._active:
            await asyncio.sleep(0.05)

    def resume(self) -> None:
        self._resume.set()

    async def state_counts(self) -> dict[str, int]:
        if not self.supported:
            return {}
        challenges = await self.platform.list_challenges()
        counts: dict[str, int] = {}
        for challenge in challenges:
            state = challenge.state.value if hasattr(challenge.state, "value") else str(challenge.state)
            counts[state] = counts.get(state, 0) + 1
        return counts

    def drain_events(self) -> list[PreparationEvent]:
        events: list[PreparationEvent] = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except asyncio.QueueEmpty:
                return events
