"""ChallengeSwarm — Parallel solvers racing on one challenge."""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from backend.agents.solver import Solver
from backend.candidate_registry import CandidateRegistry, normalize_flag
from backend.cost_tracker import CostTracker
from backend.knowledge import KnowledgeQuery, KnowledgeStore, _clean_text, record_from_result
from backend.knowledge_service import KnowledgeService
from backend.local_knowledge import normalized_keywords
from backend.message_bus import ChallengeMessageBus
from backend.models import DEFAULT_MODELS, provider_from_spec
from backend.platforms.base import PlatformAdapter
from backend.prompts import ChallengeMeta, list_distfiles
from backend.solver_base import (
    BLOCKED,
    BUDGET_EXHAUSTED,
    CANCELLED,
    CANDIDATE_FOUND,
    ERROR,
    FLAG_FOUND,
    GAVE_UP,
    NEEDS_INPUT,
    QUOTA_ERROR,
    TIMED_OUT,
    VERIFIED,
    SolverProtocol,
    SolverResult,
)

if TYPE_CHECKING:
    from backend.config import Settings
    from backend.writeups import WriteupManager

logger = logging.getLogger(__name__)


# Quota fallback: map subscription-backed providers to API-backed equivalents
QUOTA_FALLBACK: dict[str, str] = {
    "claude-sdk/claude-opus-4-6": "bedrock/us.anthropic.claude-opus-4-6-v1",
    "claude-sdk/claude-opus-4-6/medium": "bedrock/us.anthropic.claude-opus-4-6-v1",
    "claude-sdk/claude-opus-4-6/max": "bedrock/us.anthropic.claude-opus-4-6-v1",
    "codex/gpt-5.4": "azure/gpt-5.4",
    "codex/gpt-5.4-mini": "azure/gpt-5.4-mini",
    "codex/gpt-5.3-codex-spark": "zen/gpt-5.3-codex-spark",
}


def _quota_fallback_spec(model_spec: str) -> str | None:
    return QUOTA_FALLBACK.get(model_spec)


def _technique_query(findings: str) -> str:
    """Extract stable technical terms without submitting raw findings to search."""
    rules = (
        (r"\b(?:postgresql|postgres|pgsql|pg_execute_server_program|pg_roles)\b", "PostgreSQL"),
        (r"\b(?:sqlstate|sqli|sql injection)\b|SQL注入|注入点", "SQL injection"),
        (r"\b(?:boolean|blind|true.false)\b|布尔|盲注", "boolean oracle"),
        (r"\bcopy\s+(?:(?:to|from)(?:\s*/\s*(?:to|from))?|(?:\.{3}|…)\s*(?:to|from))\s+program\b|server.side program|退出状态", "COPY TO PROGRAM exit status"),
        (r"\b(?:pg_has_role|role membership|superuser)\b|角色成员|权限检查", "role membership privileges"),
        (r"\bmysql\b", "MySQL"),
        (r"\bsqlite\b", "SQLite"),
        (r"\bssrf\b", "SSRF"),
        (r"\bssti\b", "SSTI"),
        (r"\bjwt\b", "JWT"),
        (r"\blfi\b|文件包含", "LFI"),
        (r"\brce\b|命令执行", "RCE"),
    )
    terms = [term for pattern, term in rules if re.search(pattern, findings, re.IGNORECASE)]
    return " ".join(terms[:4])


@dataclass
class ChallengeSwarm:
    """Parallel solvers racing on one challenge."""

    challenge_dir: str
    meta: ChallengeMeta
    platform: PlatformAdapter
    cost_tracker: CostTracker
    settings: Settings
    model_specs: list[str] = field(default_factory=lambda: list(DEFAULT_MODELS))
    no_submit: bool = False
    coordinator_inbox: asyncio.Queue | None = None
    analysis_gateway: object | None = None
    writeup_manager: WriteupManager | None = None

    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    solvers: dict[str, SolverProtocol] = field(default_factory=dict)
    findings: dict[str, str] = field(default_factory=dict)
    auto_knowledge_queries: dict[str, set[str]] = field(default_factory=dict)
    winner: SolverResult | None = None
    confirmed_flag: str | None = None
    _flag_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _submit_count: dict[str, int] = field(default_factory=dict)  # per-model wrong submission count
    _submitted_flags: set[str] = field(default_factory=set)  # dedup exact flags
    _last_submit_time: dict[str, float] = field(default_factory=dict)  # per-model last submit timestamp
    message_bus: ChallengeMessageBus = field(default_factory=ChallengeMessageBus)
    knowledge_store: KnowledgeStore = field(init=False, repr=False)
    knowledge_service: KnowledgeService = field(init=False, repr=False)
    knowledge_context: str = field(init=False, default="", repr=False)
    candidate_registry: CandidateRegistry = field(init=False, repr=False)
    agent_states: dict[str, str] = field(default_factory=dict)
    agent_roles: dict[str, str] = field(default_factory=dict)
    agent_attempts: dict[str, int] = field(default_factory=dict)
    agent_last_activity: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        enabled = bool(getattr(self.settings, "knowledge_enabled", True))
        path = getattr(self.settings, "knowledge_db_path", ".runtime/knowledge.sqlite3")
        self.knowledge_store = KnowledgeStore(path, enabled=enabled)
        self.knowledge_service = KnowledgeService(self.settings, self.knowledge_store)
        query = KnowledgeQuery.from_meta(self.meta)
        query = replace(query, files=tuple(list_distfiles(self.challenge_dir)))
        self.knowledge_context = self.knowledge_service.initial_context(query)
        self.candidate_registry = CandidateRegistry(
            int(getattr(self.settings, "flag_verification_quorum", 2) or 2)
        )
        self.agent_roles = self._assign_roles()

    def _assign_roles(self) -> dict[str, str]:
        """Assign complementary initial roles deterministically."""
        category = (self.meta.category or "").lower()
        if category in {"pwn", "reverse", "binary"} or category in {"web", "mobile", "blockchain"}:
            roles = ["recon", "static_analysis", "dynamic_exploit", "alternative_path", "verifier"]
        else:
            roles = ["recon", "primary_analysis", "alternative_path", "verifier"]
        return {spec: roles[index % len(roles)] for index, spec in enumerate(self.model_specs)}

    def _create_solver(self, model_spec: str):
        """Create the right solver type based on provider.

        - claude-sdk/* → ClaudeSolver (Claude Agent SDK, subscription-first)
        - codex/* → CodexSolver (Codex App Server, subscription-first)
        - bedrock/*, azure/*, zen/*, google/* → Pydantic AI Solver (API)
        """
        provider = provider_from_spec(model_spec)

        def _submit_fn(flag): return self.try_submit_flag(flag, model_spec)
        _notify = self._make_notify_fn(model_spec)

        if provider == "claude-sdk":
            from backend.agents.claude_solver import ClaudeSolver
            return ClaudeSolver(
                model_spec=model_spec,
                challenge_dir=self.challenge_dir,
                meta=self.meta,
                platform=self.platform,
                cost_tracker=self.cost_tracker,
                settings=self.settings,
                cancel_event=self.cancel_event,
                no_submit=self.no_submit,
                submit_fn=_submit_fn,
                message_bus=self.message_bus,
                notify_coordinator=_notify,
                knowledge_context=self.knowledge_context,
                knowledge_service=self.knowledge_service,
                analysis_gateway=self.analysis_gateway,
            )

        if provider == "codex":
            from backend.agents.codex_solver import CodexSolver
            return CodexSolver(
                model_spec=model_spec,
                challenge_dir=self.challenge_dir,
                meta=self.meta,
                platform=self.platform,
                cost_tracker=self.cost_tracker,
                settings=self.settings,
                cancel_event=self.cancel_event,
                no_submit=self.no_submit,
                submit_fn=_submit_fn,
                message_bus=self.message_bus,
                notify_coordinator=_notify,
                knowledge_context=self.knowledge_context,
                knowledge_service=self.knowledge_service,
                analysis_gateway=self.analysis_gateway,
            )

        return self._create_pydantic_solver(model_spec)

    def _make_notify_fn(self, model_spec: str):
        """Create a callback that pushes solver messages to the coordinator inbox."""
        async def _notify(message: str) -> None:
            if self.coordinator_inbox:
                self.coordinator_inbox.put_nowait(
                    f"[{self.meta.name}/{model_spec}] {message}"
                )
        return _notify

    def _create_pydantic_solver(self, model_spec: str, sandbox=None, owns_sandbox: bool | None = None) -> Solver:
        """Create a Pydantic AI solver. Pass sandbox to reuse an existing container (quota fallback)."""
        solver = Solver(
            model_spec=model_spec,
            challenge_dir=self.challenge_dir,
            meta=self.meta,
            platform=self.platform,
            cost_tracker=self.cost_tracker,
            settings=self.settings,
            cancel_event=self.cancel_event,
            sandbox=sandbox,
            owns_sandbox=owns_sandbox,
            knowledge_context=self.knowledge_context,
            knowledge_service=self.knowledge_service,
            analysis_gateway=self.analysis_gateway,
        )
        solver.deps.message_bus = self.message_bus
        solver.deps.model_spec = model_spec
        solver.deps.no_submit = self.no_submit
        solver.deps.submit_fn = lambda flag: self.try_submit_flag(flag, model_spec)
        solver.deps.notify_coordinator = self._make_notify_fn(model_spec)
        solver.deps.analysis_gateway = self.analysis_gateway
        return solver

    def _gather_sibling_insights(self, exclude_model: str) -> str:
        parts: list[str] = []
        for model, finding in self.findings.items():
            if model != exclude_model and finding:
                role = self.agent_roles.get(model, "agent")
                parts.append(f"[{model}/{role}]: {finding}")
        return "\n\n".join(parts) if parts else "No sibling insights available yet."

    # Escalating cooldowns after incorrect submissions (per model)
    SUBMISSION_COOLDOWNS = [0, 30, 120, 300, 600]  # 0s, 30s, 2min, 5min, 10min

    async def try_submit_flag(self, flag: str, model_spec: str) -> tuple[str, bool]:
        """Cooldown-gated, deduplicated flag submission. Returns (display, is_confirmed)."""
        async with self._flag_lock:
            normalized = flag.strip()
            if self.confirmed_flag:
                if normalized == self.confirmed_flag:
                    return f"ALREADY SOLVED — flag already confirmed: {self.confirmed_flag}", True
                return "ALREADY SOLVED — a different flag was confirmed for this challenge.", False

            # Dedup exact flags across all models
            if normalized in self._submitted_flags:
                return "INCORRECT — already tried this exact flag.", False

            # Escalating cooldown after incorrect submissions
            wrong_count = self._submit_count.get(model_spec, 0)
            cooldown_idx = min(wrong_count, len(self.SUBMISSION_COOLDOWNS) - 1)
            cooldown = self.SUBMISSION_COOLDOWNS[cooldown_idx]
            if cooldown > 0:
                last_time = self._last_submit_time.get(model_spec, 0)
                elapsed = time.monotonic() - last_time
                if elapsed < cooldown:
                    remaining = int(cooldown - elapsed)
                    return (
                        f"COOLDOWN — wait {remaining}s before submitting again. "
                        f"You have {wrong_count} incorrect submissions. "
                        "Use this time to do deeper analysis and verify your flag.",
                        False,
                    )

            from backend.tools.core import do_submit_flag
            display, is_confirmed = await do_submit_flag(self.platform, self.meta.name, flag)
            # Configuration/transport failures never reached the platform. Do not
            # poison deduplication or impose an incorrect-submission cooldown.
            if display.startswith((
                "submit_flag error:", "Flag submission is disabled", "Empty flag", "DRY RUN",
            )):
                return display, False

            self._submitted_flags.add(normalized)
            if is_confirmed:
                self.confirmed_flag = normalized
            elif not display.startswith("SUBMISSION_PENDING"):
                self._submit_count[model_spec] = wrong_count + 1
                self._last_submit_time[model_spec] = time.monotonic()
            return display, is_confirmed

    async def _run_solver(self, model_spec: str) -> SolverResult | None:
        solver = self._create_solver(model_spec)
        tracer = getattr(solver, "tracer", None)
        if tracer and self.knowledge_service.initial_context_audit:
            tracer.event("knowledge_initial_context", **self.knowledge_service.initial_context_audit)
        solver.role = self.agent_roles.get(model_spec, "primary_analysis")
        self.solvers[model_spec] = solver
        self.agent_states[model_spec] = "starting"
        self.agent_last_activity[model_spec] = time.time()

        try:
            result, final_solver = await self._run_solver_loop(solver, model_spec)
            solver = final_solver
            return result
        except Exception as e:
            if "ChallengeNotReadyError" in str(e):
                result = SolverResult(
                    flag=None,
                    status=BLOCKED,
                    findings_summary=str(e),
                    step_count=0,
                    cost_usd=0.0,
                    log_path=getattr(getattr(solver, "tracer", None), "path", ""),
                )
                self.findings[model_spec] = result.findings_summary
                return result
            logger.error(f"[{self.meta.name}/{model_spec}] Fatal: {e}", exc_info=True)
            return None
        finally:
            self.agent_states[model_spec] = "finished" if not self.cancel_event.is_set() else "cancelled"
            await solver.stop()

    async def _run_solver_loop(
        self, solver: SolverProtocol, model_spec: str
    ) -> tuple[SolverResult, SolverProtocol]:
        """Inner loop: start → run → bump → run → ..."""
        bump_count = 0
        consecutive_errors = 0
        attempt_count = 0
        max_attempts = int(getattr(self.settings, "max_attempts_per_challenge", 3))
        result = SolverResult(
            flag=None, status=CANCELLED, findings_summary="",
            step_count=0, cost_usd=0.0, log_path="",
        )
        await solver.start()
        self.agent_states[model_spec] = "running"

        while not self.cancel_event.is_set():
            self.agent_attempts[model_spec] = attempt_count + 1
            self.agent_last_activity[model_spec] = time.time()
            result = await solver.run_until_done_or_gave_up()
            self.agent_last_activity[model_spec] = time.time()
            if not result.model_spec:
                result = replace(result, model_spec=solver.model_spec)

            # The sandbox workspace is removed by solver.stop(). Preserve only
            # explicitly registered EXP files while its host bind is still live.
            if result.flag and result.exp_paths and result.status in (CANDIDATE_FOUND, FLAG_FOUND, VERIFIED):
                try:
                    from backend.writeups import capture_exp_files

                    saved = capture_exp_files(
                        self.challenge_dir,
                        solver.sandbox,
                        result.exp_paths,
                        result.flag,
                        solver.model_spec,
                    )
                    result = replace(result, saved_exp_paths=tuple(saved))
                except Exception as exc:
                    logger.warning(
                        "[%s/%s] Failed to preserve EXP files: %s",
                        self.meta.name,
                        model_spec,
                        exc,
                    )

            # A proposed flag is sufficient to start writing. Do this before
            # the (possibly long-running) independent verifier; the writeup
            # itself labels the flag as unconfirmed until stronger evidence arrives.
            if result.status == CANDIDATE_FOUND and result.flag and self.writeup_manager:
                try:
                    await self.writeup_manager.record_and_schedule(
                        self.challenge_dir,
                        self.meta,
                        result.flag.strip(),
                        "candidate_found",
                        solver_result=result,
                        model_spec=(getattr(self.settings, "writeup_model_spec", "")
                                    or result.model_spec or model_spec),
                    )
                except Exception:
                    logger.exception("[%s/%s] Could not queue candidate writeup", self.meta.name, model_spec)

            max_cost = float(getattr(self.settings, "solver_max_cost_usd", 0) or 0)
            observed_cost = max(result.cost_usd, result.total_cost_usd)
            if max_cost and observed_cost >= max_cost and result.status not in (FLAG_FOUND, VERIFIED):
                result = replace(
                    result,
                    status=BUDGET_EXHAUSTED,
                    findings_summary=(result.findings_summary + " | Cost budget exhausted")[:2000],
                )

            # A zero-work quota failure is an infrastructure handoff, not a solving attempt.
            if not (
                result.status == QUOTA_ERROR
                and result.step_count == 0
                and result.cost_usd == 0
            ):
                attempt_count += 1

            record = record_from_result(
                self.meta,
                result,
                model_spec,
                confirmed=bool(
                    self.confirmed_flag
                    and result.flag
                    and result.flag.strip() == self.confirmed_flag
                ),
            )
            if record:
                inserted = self.knowledge_store.remember(record)
                if inserted:
                    logger.info(
                        "[%s/%s] Stored solving knowledge (%s)",
                        self.meta.name,
                        model_spec,
                        record.outcome,
                    )

            # Only broadcast useful findings — skip errors and broken solvers
            if (result.status not in (ERROR, QUOTA_ERROR)
                    and not (result.step_count == 0 and result.cost_usd == 0)
                    and result.findings_summary
                    and not result.findings_summary.startswith(("Error:", "Turn failed:"))):
                self.findings[model_spec] = result.findings_summary
                await self.message_bus.post_event(
                    model_spec,
                    "finding",
                    result.findings_summary[:1000],
                    role=self.agent_roles.get(model_spec, ""),
                    evidence=result.evidence,
                )

            if result.status in (CANDIDATE_FOUND,) and result.flag:
                self.candidate_registry.propose(
                    result.flag,
                    model_spec,
                    method=result.findings_summary[:500],
                    evidence=result.evidence,
                )
                # A proposal from a distinct solver is an independent
                # verification vote. Repeated attempts by one solver do not
                # increase the quorum because sources are stored as a set.
                self.candidate_registry.verify(
                    result.flag,
                    model_spec,
                    accepted=True,
                    evidence=result.evidence,
                )
                if not self.candidate_registry.verified(result.flag):
                    await self._run_independent_verifier(
                        model_spec,
                        result.flag,
                        result.evidence,
                    )
                verified = self.candidate_registry.verified(result.flag)
                if verified:
                    result = replace(
                        result,
                        status=VERIFIED,
                        verified_by=tuple(sorted(verified.accepted_sources)),
                        findings_summary=(
                            result.findings_summary
                            + f" | Independently verified by {', '.join(sorted(verified.accepted_sources))}"
                        )[:2000],
                    )
                else:
                    self.agent_states[model_spec] = "candidate_pending_verification"
                    await self.message_bus.post_event(
                        model_spec,
                        "candidate",
                        f"Candidate pending independent verification: {normalize_flag(result.flag)}",
                        role=self.agent_roles.get(model_spec, ""),
                        confidence=0.5,
                        evidence=result.evidence,
                    )
                    await self._make_notify_fn(model_spec)(
                        f"Candidate Flag from role {self.agent_roles.get(model_spec, 'agent')} "
                        f"is pending independent verification: {normalize_flag(result.flag)}"
                    )

            if result.status in (FLAG_FOUND, VERIFIED):
                self.cancel_event.set()
                self.winner = result
                self.agent_states[model_spec] = "won"
                logger.info(
                    f"[{self.meta.name}] Flag found by {model_spec}: {result.flag}"
                )
                return result, solver

            if result.status == CANDIDATE_FOUND:
                # Continue with a bounded new attempt so the proposing solver
                # can produce verification evidence, while other solvers run.
                result = replace(result, status=GAVE_UP)

            if result.status in (BLOCKED, NEEDS_INPUT):
                logger.warning("[%s] Solver blocked: %s", self.meta.name, result.findings_summary)
                notify = self._make_notify_fn(model_spec)
                await notify(
                    f"Solver ended with {result.status}: {result.findings_summary[:500]}"
                )
                return result, solver

            if result.status == CANCELLED:
                break

            # Quota exhaustion: fall back to API-backed Pydantic AI solver
            if result.status == QUOTA_ERROR:
                fallback_spec = _quota_fallback_spec(model_spec)
                if fallback_spec:
                    logger.warning(
                        f"[{self.meta.name}/{model_spec}] Quota exhausted — falling back to {fallback_spec}"
                    )
                    existing_sandbox = solver.detach_sandbox()
                    await solver.stop()
                    solver = self._create_pydantic_solver(fallback_spec, sandbox=existing_sandbox, owns_sandbox=True)
                    solver.role = self.agent_roles.get(model_spec, "primary_analysis")
                    self.solvers[model_spec] = solver
                    await solver.start()
                    attempt_count = 0
                    continue
                # No fallback available, treat as error
                break

            if result.status in (GAVE_UP, ERROR, TIMED_OUT, BUDGET_EXHAUSTED):
                if result.step_count == 0 and result.cost_usd == 0:
                    logger.warning(
                        f"[{self.meta.name}/{model_spec}] Broken (0 steps, $0) — not bumping"
                    )
                    break

                if attempt_count >= max_attempts:
                    logger.info(
                        "[%s/%s] Reached attempt limit (%d)",
                        self.meta.name,
                        model_spec,
                        max_attempts,
                    )
                    break

                # Track consecutive errors — stop after 3 in a row
                if result.status == ERROR:
                    consecutive_errors += 1
                    if consecutive_errors >= 3:
                        logger.warning(
                            f"[{self.meta.name}/{model_spec}] {consecutive_errors} consecutive errors — giving up"
                        )
                        break
                else:
                    consecutive_errors = 0

                bump_count += 1
                # Cooldown between bumps — check cancellation during wait
                try:
                    await asyncio.wait_for(
                        self.cancel_event.wait(),
                        timeout=min(bump_count * 30, 300),
                    )
                    break  # cancelled during cooldown
                except TimeoutError:
                    pass  # cooldown elapsed, proceed with bump
                insights = self._gather_sibling_insights(model_spec)
                if (result.findings_summary and result.step_count > 0
                        and not result.findings_summary.startswith(("Error:", "Turn failed:"))):
                    query = _technique_query(result.findings_summary)
                    key = normalized_keywords(query)
                    seen = self.auto_knowledge_queries.setdefault(model_spec, set())
                    if key and key not in seen:
                        seen.add(key)
                        hits = await self.knowledge_service.search_async(query, category=self.meta.category, limit=3)
                        tracer = getattr(solver, "tracer", None)
                        if tracer:
                            tracer.event("knowledge_auto_search", keywords=key,
                                         external_snapshot=self.knowledge_service.external.snapshot_id,
                                         local_snapshot=self.knowledge_service.local.snapshot_id,
                                         hits=len(hits), errors=list(getattr(hits, "errors", ())),
                                         document_ids=[hit["document_id"] for hit in hits])
                        lines = ["<knowledge_reference_untrusted>"]
                        for hit in hits[:3]:
                            verification = hit.get("verification_status") or hit.get("outcome") or "unverified"
                            entry = (f"[{hit['source']}; {verification}] {hit['document_id']} {hit['path']}: "
                                     f"{_clean_text(hit['snippet'])[:320]}")
                            if len("\n".join((*lines, entry, "</knowledge_reference_untrusted>"))) > 1200:
                                break
                            lines.append(entry)
                        if len(lines) > 1:
                            insights += "\n\nRelevant offline knowledge:\n" + "\n".join((*lines, "</knowledge_reference_untrusted>"))
                    elif tracer := getattr(solver, "tracer", None):
                        tracer.event("knowledge_auto_skipped", reason="duplicate_or_no_terms")
                elif tracer := getattr(solver, "tracer", None):
                    tracer.event("knowledge_auto_skipped", reason="no_substantive_findings")
                solver.bump(insights)
                logger.info(
                    f"[{self.meta.name}/{model_spec}] Bumped ({bump_count}), resuming"
                )
                continue

        return result, solver

    async def _run_independent_verifier(
        self,
        model_spec: str,
        flag: str,
        evidence: tuple[str, ...] = (),
    ) -> None:
        """Verify one candidate in a fresh backend session and sandbox.

        The verifier is intentionally not inserted into ``self.solvers``: it
        is a short-lived independent task, not another long-running worker.
        It receives no original message history and therefore cannot simply
        repeat the proposing model's conclusion.
        """
        verifier_spec = f"{model_spec}#verifier"
        verifier = self._create_solver(model_spec)
        verifier.role = "verifier"
        self.agent_states[verifier_spec] = "verifying"
        self.agent_roles[verifier_spec] = "verifier"
        self.agent_last_activity[verifier_spec] = time.time()
        try:
            await verifier.start()
            verifier.bump(
                "You are an independent verifier. Do not trust the previous solver. "
                f"Reproduce or disprove this candidate Flag: {normalize_flag(flag)}.\n"
                f"Original evidence (untrusted): {list(evidence)[:5]}\n"
                "Only report a candidate if you can independently derive the exact same value. "
                "Otherwise explain why it is rejected or inconclusive."
            )
            result = await verifier.run_until_done_or_gave_up()
            self.agent_last_activity[verifier_spec] = time.time()
            if (
                result.status in (CANDIDATE_FOUND, FLAG_FOUND, VERIFIED)
                and result.flag
                and normalize_flag(result.flag) == normalize_flag(flag)
            ):
                self.candidate_registry.verify(
                    flag,
                    verifier_spec,
                    accepted=True,
                    evidence=result.evidence or (result.findings_summary[:1000],),
                )
            else:
                self.candidate_registry.verify(
                    flag,
                    verifier_spec,
                    accepted=False,
                    evidence=(result.findings_summary[:1000],),
                )
        except Exception as exc:
            logger.warning(
                "[%s/%s] Independent verification failed: %s",
                self.meta.name,
                model_spec,
                exc,
            )
            self.candidate_registry.verify(
                flag,
                verifier_spec,
                accepted=False,
                evidence=(f"verifier error: {exc}",),
            )
        finally:
            self.agent_states[verifier_spec] = "finished"
            await verifier.stop()

    async def run(self) -> SolverResult | None:
        """Run all solvers in parallel. Returns the winner's result or None."""
        task_models = {
            asyncio.create_task(self._run_solver(spec), name=f"solver-{spec}"): spec
            for spec in self.model_specs
        }
        tasks = list(task_models)
        completed: dict[str, SolverResult] = {}

        try:
            while tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                for task in done:
                    try:
                        result = task.result()
                    except Exception:
                        continue
                    if result:
                        completed[task_models[task]] = result
                    if result and result.status in (FLAG_FOUND, VERIFIED):
                        self.cancel_event.set()
                        for p in pending:
                            p.cancel()
                        await asyncio.gather(*pending, return_exceptions=True)
                        return result

                tasks = list(pending)

            self.cancel_event.set()
            if self.winner:
                return self.winner
            if not completed:
                return None
            statuses = "; ".join(
                f"{model}: {result.status} ({result.findings_summary[:300]})"
                for model, result in completed.items()
            )
            representative = next(
                (
                    result
                    for result in completed.values()
                    if result.status in (NEEDS_INPUT, BLOCKED)
                ),
                next(iter(completed.values())),
            )
            return SolverResult(
                flag=None,
                status=representative.status,
                findings_summary=f"All solvers finished without a confirmed flag. {statuses}",
                step_count=sum(result.step_count for result in completed.values()),
                cost_usd=sum(result.cost_usd for result in completed.values()),
                log_path=representative.log_path,
            )
        except Exception as e:
            logger.error(f"[{self.meta.name}] Swarm error: {e}", exc_info=True)
            self.cancel_event.set()
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            return None

    def kill(self) -> None:
        """Cancel all agents for this challenge."""
        self.cancel_event.set()

    def get_status(self) -> dict:
        """Get per-agent progress and findings."""
        return {
            "challenge": self.meta.name,
            "cancelled": self.cancel_event.is_set(),
            "winner": self.winner.flag if self.winner else None,
            "candidates": self.candidate_registry.snapshot(),
            "agents": {
                spec: {
                    "findings": self.findings.get(spec, ""),
                    "status": self.agent_states.get(spec, "pending"),
                    "role": self.agent_roles.get(spec, "primary_analysis"),
                    "attempt": self.agent_attempts.get(spec, 0),
                    "last_activity": self.agent_last_activity.get(spec),
                }
                for spec in self.model_specs
            },
        }
