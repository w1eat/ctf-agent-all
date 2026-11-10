"""Background CTFd poller — detects new and solved challenges every 5 seconds."""

import asyncio
import logging
from dataclasses import dataclass, field

from backend.platforms.base import PlatformAdapter

logger = logging.getLogger(__name__)


@dataclass
class PollEvent:
    kind: str  # "new_challenge" | "challenge_available" | "challenge_unlocked" | "challenge_solved"
    challenge_name: str
    details: dict = field(default_factory=dict)


@dataclass
class CTFdPoller:
    """Polls CTFd every interval_s seconds, emits events for new/solved challenges."""

    platform: PlatformAdapter
    interval_s: float = 5.0

    _known_challenges: set[str] = field(default_factory=set)
    _known_solved: set[str] = field(default_factory=set)
    _known_by_id: dict[str, tuple[str, bool | None]] = field(default_factory=dict)
    _event_queue: asyncio.Queue[PollEvent] = field(default_factory=asyncio.Queue)
    _task: asyncio.Task | None = field(default=None, repr=False)
    _stop: asyncio.Event = field(default_factory=asyncio.Event)

    async def start(self) -> None:
        """Do initial poll (silent — no events) and start the background loop."""
        await self._seed()
        logger.info(
            "Poller initialized: %d challenges, %d solved",
            len(self._known_challenges),
            len(self._known_solved),
        )
        self._task = asyncio.create_task(self._loop(), name="ctfd-poller")

    async def _seed(self) -> None:
        """Initial fetch — just populate known state, no events."""
        challenges = await self.platform.list_challenges()
        self._known_by_id = self._snapshot(challenges)
        self._known_challenges = {challenge.name for challenge in challenges}
        self._known_solved = (await self.platform.get_solve_status()) & self._known_challenges

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass

    async def get_event(self, timeout: float = 1.0) -> PollEvent | None:
        """Non-blocking get — returns None if no event within timeout."""
        try:
            return await asyncio.wait_for(self._event_queue.get(), timeout=timeout)
        except (TimeoutError, asyncio.CancelledError):
            return None

    def wake(self) -> None:
        """Wake the coordinator when a solver has a pending request."""
        self._event_queue.put_nowait(PollEvent("coordination_request", ""))

    def drain_events(self) -> list[PollEvent]:
        """Drain all pending events without blocking."""
        events: list[PollEvent] = []
        while not self._event_queue.empty():
            try:
                events.append(self._event_queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return events

    @property
    def known_challenges(self) -> set[str]:
        return set(self._known_challenges)

    @property
    def known_solved(self) -> set[str]:
        return set(self._known_solved)

    @staticmethod
    def _snapshot(challenges) -> dict[str, tuple[str, bool | None]]:
        snapshot = {}
        for challenge in challenges:
            name = str(challenge.name)
            native_id = str(getattr(challenge, "native_id", "") or name)
            source_data = getattr(challenge, "source_data", None) or {}
            locked = source_data.get("locked")
            if not isinstance(locked, bool):
                locked = None
            if native_id in snapshot and snapshot[native_id][0] != name:
                raise ValueError(f"Duplicate challenge ID {native_id!r}")
            snapshot[native_id] = (name, locked)
        return snapshot

    async def _poll_once(self) -> None:
        try:
            challenges = await self.platform.list_challenges()
            current_by_id = self._snapshot(challenges)
            current_names = {challenge.name for challenge in challenges}
            current_solved = (await self.platform.get_solve_status()) & current_names

            # Sanity check: if results look bogus compared to what we know, skip.
            if self._known_challenges and len(current_names) < len(self._known_challenges) // 2:
                logger.warning(f"Poll returned suspicious data ({len(current_names)} challenges vs {len(self._known_challenges)} known) — skipping")
                return
            # Don't let solved count regress (API might return empty on errors)
            if self._known_solved and not current_solved:
                logger.warning("Poll returned 0 solved (had %d) — skipping", len(self._known_solved))
                return

            # Detect new challenges
            for native_id in current_by_id.keys() - self._known_by_id.keys():
                name, locked = current_by_id[native_id]
                logger.info("New challenge detected: %s", name)
                self._event_queue.put_nowait(
                    PollEvent("new_challenge", name, {"native_id": native_id, "locked": locked})
                )

            for native_id in current_by_id.keys() & self._known_by_id.keys():
                name, locked = current_by_id[native_id]
                previous_locked = self._known_by_id[native_id][1]
                if locked is False and previous_locked is not False:
                    logger.info("Challenge became available: %s", name)
                    kind = "challenge_unlocked" if previous_locked is True else "challenge_available"
                    self._event_queue.put_nowait(
                        PollEvent(kind, name, {"native_id": native_id})
                    )

            # Detect newly solved
            new_solves = current_solved - self._known_solved
            for name in new_solves:
                logger.info("Challenge solved: %s", name)
                self._event_queue.put_nowait(
                    PollEvent("challenge_solved", name)
                )

            self._known_challenges = current_names
            self._known_solved = current_solved
            self._known_by_id = current_by_id

        except Exception as e:
            logger.warning(f"Poll error: {e}")

    async def _loop(self) -> None:
        while not self._stop.is_set():
            await asyncio.sleep(self.interval_s)
            await self._poll_once()
