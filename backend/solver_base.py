"""Solver result type, status constants, and solver protocol — shared across all backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from backend.sandbox import DockerSandbox

# Status constants
FLAG_FOUND = "flag_found"
# A model-proposed flag is not a solved challenge until it is independently
# verified.  FLAG_FOUND is retained as a compatibility alias for platform
# confirmations and older solver implementations.
CANDIDATE_FOUND = "candidate_found"
VERIFIED = "verified"
REJECTED_CANDIDATE = "rejected_candidate"
TIMED_OUT = "timed_out"
BUDGET_EXHAUSTED = "budget_exhausted"
PROGRESS = "progress"
BLOCKED = "blocked"
NEEDS_INPUT = "needs_input"
GAVE_UP = "gave_up"
CANCELLED = "cancelled"
ERROR = "error"
QUOTA_ERROR = "quota_error"

# Flag confirmation markers from CTFd
CORRECT_MARKERS = ("CORRECT", "ALREADY SOLVED")


@dataclass
class SolverResult:
    flag: str | None
    status: str
    findings_summary: str
    step_count: int
    cost_usd: float
    log_path: str
    # Optional fields are appended to preserve compatibility with the original
    # six-field positional constructor used by integrations and tests.
    evidence: tuple[str, ...] = ()
    role: str = ""
    attempt_id: str = ""
    verified_by: tuple[str, ...] = ()
    total_cost_usd: float = 0.0
    solution_steps: tuple[str, ...] = ()
    exp_paths: tuple[str, ...] = ()
    exp_run_command: str = ""
    saved_exp_paths: tuple[str, ...] = ()
    model_spec: str = ""

    @property
    def is_candidate(self) -> bool:
        """Whether this result proposes a flag without proving it."""
        return self.status in {CANDIDATE_FOUND, FLAG_FOUND} and bool(self.flag)

    @property
    def is_verified(self) -> bool:
        """Whether this result is safe to use as a final challenge result."""
        return self.status == VERIFIED or self.status == FLAG_FOUND and bool(self.verified_by)


class SolverProtocol(Protocol):
    """Common interface for all solver backends (Pydantic AI, Claude SDK, Codex)."""

    model_spec: str
    agent_name: str
    role: str
    sandbox: DockerSandbox | None

    async def start(self) -> None: ...
    async def run_until_done_or_gave_up(self) -> SolverResult: ...
    def bump(self, insights: str) -> None: ...
    def detach_sandbox(self) -> DockerSandbox | None: ...
    async def stop(self) -> None: ...
