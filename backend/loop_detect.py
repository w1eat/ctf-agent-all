"""Tool signature tracking for loop detection."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field


@dataclass
class LoopDetector:
    """Track recent tool call signatures to detect repetitive loops."""

    window: int = 12
    warn_threshold: int = 3
    break_threshold: int = 5
    _recent: deque[str] = field(init=False)

    def __post_init__(self) -> None:
        self._recent = deque(maxlen=self.window)

    def check(self, tool_name: str, args: dict | str | None = None) -> str | None:
        """Check if the agent is stuck in a loop.

        Returns:
            None: no loop
            "warn": approaching loop threshold
            "break": exceeded loop threshold, should force-break
        """
        if args:
            raw = json.dumps(args, sort_keys=True) if isinstance(args, dict) else str(args)
            sig = f"{tool_name}:{raw[:500]}"
        else:
            sig = tool_name
        self._recent.append(sig)

        count = sum(1 for s in self._recent if s == sig)
        if count >= self.break_threshold:
            return "break"
        if count >= self.warn_threshold:
            return "warn"
        return None

    @property
    def last_sig(self) -> str:
        return self._recent[-1] if self._recent else ""

    def reset(self) -> None:
        self._recent.clear()


LOOP_WARNING_MESSAGE = (
    "⚠️ **You are stuck in a loop** — you have run the exact same command multiple times "
    "with identical results. STOP repeating this command. Step back, reconsider your approach, "
    "and try a **completely different** technique or tool. "
    "If you were grepping/searching, try a Python script instead. "
    "If you were analyzing one aspect of the file, switch to another. "
    "What other angles haven't you explored?"
)
