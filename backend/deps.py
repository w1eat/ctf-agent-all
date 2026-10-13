"""Shared dependency types — avoids circular imports between agents and tools."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from backend.cost_tracker import CostTracker
from backend.platforms.base import PlatformAdapter
from backend.sandbox import DockerSandbox

if TYPE_CHECKING:
    from backend.message_bus import ChallengeMessageBus

# Type for the deduped submit callback: (flag) -> (display, is_confirmed)
SubmitFn = Callable[[str], Coroutine[Any, Any, tuple[str, bool]]]


@dataclass
class SolverDeps:
    sandbox: DockerSandbox
    platform: PlatformAdapter
    challenge_dir: str
    challenge_name: str
    workspace_dir: str
    use_vision: bool
    cost_tracker: CostTracker | None = None
    confirmed_flag: str | None = None
    message_bus: ChallengeMessageBus | None = None
    model_spec: str = ""
    submit_fn: SubmitFn | None = None  # Deduped flag submission via swarm
    no_submit: bool = False
    notify_coordinator: Callable[[str], Coroutine[Any, Any, None]] | None = None
    analysis_gateway: Any | None = None
    knowledge_service: Any | None = None
    knowledge_query_budget: Any | None = None
    knowledge_tracer: Any | None = None


@dataclass
class CoordinatorDeps:
    platform: PlatformAdapter
    cost_tracker: CostTracker
    settings: Any
    model_specs: list[str] = field(default_factory=list)
    challenges_root: str = "challenges"
    no_submit: bool = False
    max_concurrent_challenges: int = 10
    challenge_types: set[str] = field(default_factory=set)

    msg_port: int = 0  # 0 = auto-pick free port
    tracer: Any | None = None
    defer_trace_close: bool = False
    analysis_gateway: Any | None = None
    writeup_manager: Any | None = None
    coordinator_model_spec: str = ""

    # Runtime state
    submission_setup_complete: bool = False
    coordinator_inbox: asyncio.Queue = field(default_factory=asyncio.Queue)
    operator_inbox: asyncio.Queue = field(default_factory=asyncio.Queue)
    swarms: dict[str, Any] = field(default_factory=dict)
    swarm_tasks: dict[str, asyncio.Task] = field(default_factory=dict)
    results: dict[str, dict] = field(default_factory=dict)
    challenge_dirs: dict[str, str] = field(default_factory=dict)
    challenge_metas: dict[str, Any] = field(default_factory=dict)
    pending_challenges: dict[str, str] = field(default_factory=dict)
    pending_since: dict[str, float] = field(default_factory=dict)
    deferred_auto_spawn: set[str] = field(default_factory=set)
    reported_finished_swarms: set[str] = field(default_factory=set)
    selected_challenges: set[str] = field(default_factory=set)
