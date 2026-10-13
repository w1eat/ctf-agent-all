"""Per-model solver agent — one model, one container, one challenge."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, cast

from pydantic_ai import Agent, PromptedOutput, RunContext
from pydantic_ai.messages import ModelRequest, UserPromptPart
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai.toolsets.abstract import ToolsetTool
from pydantic_ai.toolsets.wrapper import WrapperToolset

from backend.config import Settings
from backend.cost_tracker import CostTracker
from backend.deps import SolverDeps
from backend.loop_detect import LOOP_WARNING_MESSAGE, LoopDetector
from backend.models import (
    model_id_from_spec,
    provider_from_spec,
    resolve_model,
    resolve_model_settings,
    supports_vision,
)
from backend.output_types import (
    CandidateFound,
    FlagFound,
    SolverBlocked,
    SolverGaveUp,
    SolverNeedsInput,
    SolverOutput,
)
from backend.platforms.base import PlatformAdapter
from backend.prompts import ChallengeMeta, build_prompt, list_distfiles
from backend.sandbox import DockerSandbox
from backend.solver_base import (
    BLOCKED,
    BUDGET_EXHAUSTED,
    CANCELLED,
    CANDIDATE_FOUND,
    CORRECT_MARKERS,
    ERROR,
    FLAG_FOUND,
    GAVE_UP,
    NEEDS_INPUT,
    TIMED_OUT,
    SolverResult,
)
from backend.tools.analysis import analysis_status, call_analysis_tool, list_analysis_tools
from backend.tools.flag import confirm_submission, submit_flag
from backend.tools.knowledge import read_knowledge, search_knowledge, stage_knowledge_script
from backend.tools.sandbox import (
    bash,
    check_findings,
    list_files,
    notify_coordinator,
    read_file,
    web_fetch,
    webhook_create,
    webhook_get_requests,
    write_file,
)
from backend.tools.vision import view_image
from backend.tracing import SolverTracer

logger = logging.getLogger(__name__)


class ToolBudgetExceededError(RuntimeError):
    """Raised before a tool call when an attempt used its step budget."""


@dataclass
class TracingToolset(WrapperToolset[SolverDeps]):
    """Wraps a toolset to add per-call tracing and loop detection."""

    tracer: SolverTracer = field(repr=False)
    loop_detector: LoopDetector = field(repr=False)
    step_counter: list[int] = field(repr=False)
    max_steps: int = 0
    attempt_start: list[int] = field(default_factory=lambda: [0], repr=False)

    async def call_tool(
        self, name: str, tool_args: dict[str, Any], ctx: RunContext[SolverDeps], tool: ToolsetTool[SolverDeps]
    ) -> Any:
        self.step_counter[0] += 1
        step = self.step_counter[0]

        if self.max_steps and step - self.attempt_start[0] > self.max_steps:
            self.step_counter[0] -= 1
            raise ToolBudgetExceededError(f"tool-step budget exhausted at {self.max_steps} steps")

        self.tracer.tool_call(name, tool_args, step)

        # Loop detection
        loop_status = self.loop_detector.check(name, tool_args)
        if loop_status == "break":
            logger.warning(f"Loop break on {name} at step {step}")
            self.tracer.event("loop_break", tool=name, step=step)
            # Inject loop warning by returning it as the tool result
            return LOOP_WARNING_MESSAGE

        result = await self.wrapped.call_tool(name, tool_args, ctx, tool)

        result_str = str(result) if result is not None else ""
        self.tracer.tool_result(name, result_str, step)

        # Inject loop warning alongside result on "warn" level
        if loop_status == "warn":
            result = f"{result}\n\n{LOOP_WARNING_MESSAGE}" if isinstance(result, str) else result

        # Check for confirmed flag
        if (
            name in {"submit_flag", "confirm_submission"}
            and result_str.lstrip().startswith(CORRECT_MARKERS)
            and ctx.deps.confirmed_flag == str(tool_args.get("flag", "")).strip()
        ):
            self.tracer.event("flag_confirmed", tool=name, step=step)

        if step % 5 == 0 and ctx.deps.message_bus and isinstance(result, str):
            from backend.tools.core import do_check_findings
            findings_text = await do_check_findings(ctx.deps.message_bus, ctx.deps.model_spec)
            if findings_text and "No new findings" not in findings_text:
                result = f"{result}\n\n---\n{findings_text}"
                self.tracer.event("findings_injected", step=step)

        return result


def _build_toolset(deps: SolverDeps) -> FunctionToolset[SolverDeps]:
    """Build the raw toolset for a solver agent."""
    tools = [bash, read_file, write_file, list_files, submit_flag, confirm_submission, web_fetch,
             webhook_create, webhook_get_requests, check_findings, notify_coordinator]
    if deps.use_vision:
        tools.append(view_image)
    if deps.analysis_gateway:
        tools.extend([list_analysis_tools, call_analysis_tool, analysis_status])
    if getattr(deps, "knowledge_service", None):
        tools.extend([search_knowledge, read_knowledge, stage_knowledge_script])
    return FunctionToolset(tools=tools, max_retries=4)


def _output_type_for_model(model_spec: str):
    """Use prompted JSON for reasoning APIs that reject forced output tools."""
    output_type = SolverOutput
    if provider_from_spec(model_spec) == "deepseek":
        # Pydantic AI accepts a PEP 604 union here at runtime, but its generic
        # constructor annotation cannot express that union to static checkers.
        return PromptedOutput(cast(Any, output_type))
    return output_type


class Solver:
    """A single solver: one model, one container, one challenge."""

    def __init__(
        self,
        model_spec: str,
        challenge_dir: str,
        meta: ChallengeMeta,
        platform: PlatformAdapter,
        cost_tracker: CostTracker,
        settings: Settings,
        cancel_event: asyncio.Event | None = None,
        sandbox: DockerSandbox | None = None,
        owns_sandbox: bool | None = None,
        knowledge_context: str = "",
        knowledge_service: Any | None = None,
        analysis_gateway: Any | None = None,
    ) -> None:
        self.model_spec = model_spec
        self.model_id = model_id_from_spec(model_spec)
        self.challenge_dir = challenge_dir
        self.meta = meta
        self.platform = platform
        self.cost_tracker = cost_tracker
        self.settings = settings
        self.knowledge_context = knowledge_context
        self.knowledge_service = knowledge_service
        from backend.knowledge_service import KnowledgeQueryBudget

        self.knowledge_query_budget = KnowledgeQueryBudget(knowledge_service) if knowledge_service else None
        self.analysis_gateway = analysis_gateway
        self.role = ""
        self.cancel_event = cancel_event or asyncio.Event()
        self._owns_sandbox = owns_sandbox if owns_sandbox is not None else (sandbox is None)

        self.sandbox: DockerSandbox | None = sandbox or DockerSandbox(
            image=getattr(settings, "sandbox_image", "ctf-sandbox"),
            challenge_dir=challenge_dir,
            memory_limit=getattr(settings, "container_memory_limit", "4g"),
        )
        self.use_vision = supports_vision(model_spec)
        self.deps = SolverDeps(
            sandbox=self.sandbox,
            platform=platform,
            challenge_dir=challenge_dir,
            challenge_name=meta.name,
            workspace_dir="",
            use_vision=self.use_vision,
            cost_tracker=cost_tracker,
            analysis_gateway=analysis_gateway,
            knowledge_service=knowledge_service,
            knowledge_query_budget=self.knowledge_query_budget,
        )
        self.loop_detector = LoopDetector()
        self.tracer = SolverTracer(meta.name, self.model_id)
        self.tracer.knowledge_snapshots = {
            "external": knowledge_service.external.snapshot_id if knowledge_service else "",
            "local": knowledge_service.local.snapshot_id if knowledge_service else "",
        }
        self.deps.knowledge_tracer = self.tracer
        self.agent_name = f"{meta.name}/{self.model_id}"
        self._agent: Agent[SolverDeps, SolverOutput] | None = None
        self._messages: list = []
        self._step_count = [0]  # mutable ref shared with TracingToolset
        self._attempt_start_step = [0]
        self._flag: str | None = None
        self._confirmed: bool = False
        self._findings: str = ""
        self._evidence: tuple[str, ...] = ()
        self._solution_steps: tuple[str, ...] = ()
        self._exp_paths: tuple[str, ...] = ()
        self._exp_run_command: str = ""

    async def start(self) -> None:
        """Start the sandbox and build the agent."""
        self._validate_challenge_package()
        assert self.sandbox is not None
        if not self.sandbox._container:
            await self.sandbox.start()
        self.deps.workspace_dir = self.sandbox.workspace_dir

        arch_result = await self.sandbox.exec("uname -m", timeout_s=10)
        container_arch = arch_result.stdout.strip() or "unknown"
        ghidra_result = await self.sandbox.exec(
            "command -v ghidra-headless >/dev/null && test -f /opt/ghidra/support/analyzeHeadless",
            timeout_s=10,
        )

        distfile_names = list_distfiles(self.challenge_dir)
        system_prompt = build_prompt(
            self.meta,
            distfile_names,
            container_arch=container_arch,
            knowledge_context=self.knowledge_context,
            role=self.role,
            has_analysis_tools=self.analysis_gateway is not None,
            has_ghidra=ghidra_result.exit_code == 0,
        )

        model = resolve_model(self.model_spec, self.settings)
        model_settings = resolve_model_settings(self.model_spec)
        raw_toolset = _build_toolset(self.deps)
        toolset = TracingToolset(
            wrapped=raw_toolset,
            tracer=self.tracer,
            loop_detector=self.loop_detector,
            step_counter=self._step_count,
            max_steps=int(getattr(self.settings, "solver_max_tool_steps_per_attempt", 0) or 0),
            attempt_start=self._attempt_start_step,
        )

        self._agent = Agent(
            model,
            deps_type=SolverDeps,
            system_prompt=system_prompt,
            model_settings=model_settings,
            toolsets=[toolset],
            output_type=_output_type_for_model(self.model_spec),
        )

        self.tracer.event(
            "start", challenge=self.meta.name, model=self.model_id,
            run_id=str(getattr(self.settings, "challenge_run_id", "") or ""),
        )
        logger.info(f"[{self.agent_name}] Solver started")

    def _validate_challenge_package(self) -> None:
        """Fail before Docker/model startup when the current package is incomplete."""
        from pathlib import Path

        distfiles = Path(self.challenge_dir) / "distfiles"
        has_files = bool(list_distfiles(self.challenge_dir))
        has_remote = bool(self.meta.connection_info or self.meta.environment)
        mode = (self.meta.challenge_mode or "").lower()
        if mode in {"attachment", "hybrid"} and not has_files:
            raise RuntimeError("ChallengeNotReadyError: attachment package is empty")
        if mode == "remote" and not has_remote:
            raise RuntimeError("ChallengeNotReadyError: remote environment is missing")
        if mode in {"", "unknown"} and not has_files and not has_remote:
            raise RuntimeError(
                f"ChallengeNotReadyError: no attachment or environment for {self.meta.name}; "
                f"expected {distfiles}"
            )

    async def run_until_done_or_gave_up(self) -> SolverResult:
        """Run the solver loop until flag found, gave up, or cancelled."""
        if not self._agent:
            await self.start()
        assert self._agent is not None
        if self.knowledge_query_budget:
            self.knowledge_query_budget.reset()
        self._findings = ""
        if not self._confirmed:
            self._flag = None
            self._evidence = ()
            self._solution_steps = ()
            self._exp_paths = ()
            self._exp_run_command = ""

        t0 = time.monotonic()
        self._attempt_start_step[0] = self._step_count[0]

        try:
            from pydantic_ai.usage import UsageLimits
            timeout_s = int(getattr(self.settings, "solver_attempt_timeout_seconds", 0) or 0)
            run_coro = self._agent.run(
                "Solve this CTF challenge." if not self._messages else "Continue solving.",
                deps=self.deps,
                message_history=self._messages if self._messages else None,
                usage_limits=UsageLimits(request_limit=None),
            )
            result = await asyncio.wait_for(run_coro, timeout=timeout_s) if timeout_s else await run_coro

            duration = time.monotonic() - t0
            usage = result.usage

            self.cost_tracker.record(
                self.agent_name, usage, self.model_id,
                provider_spec=provider_from_spec(self.model_spec),
                duration_seconds=duration,
            )

            agent_usage = self.cost_tracker.by_agent.get(self.agent_name)
            self.tracer.usage(
                usage.input_tokens, usage.output_tokens,
                usage.cache_read_tokens,
                agent_usage.cost_usd if agent_usage else 0.0,
            )

            self._messages = result.all_messages()

            # Trace model responses from new messages
            from pydantic_ai.messages import ModelResponse, TextPart
            for msg in result.new_messages():
                if isinstance(msg, ModelResponse):
                    text_parts = [p.content for p in msg.parts if isinstance(p, TextPart)]
                    text = " ".join(text_parts)
                    msg_usage = msg.usage
                    self.tracer.model_response(
                        text[:500], self._step_count[0],
                        input_tokens=msg_usage.input_tokens if msg_usage else 0,
                        output_tokens=msg_usage.output_tokens if msg_usage else 0,
                    )

            output = result.output
            if isinstance(output, (FlagFound, CandidateFound)):
                confirmed_flag = self.deps.confirmed_flag
                same_flag = not confirmed_flag or output.flag.strip() == confirmed_flag.strip()
                self._flag = confirmed_flag or output.flag
                self._findings = f"Flag found via {output.method}: {self._flag}" if same_flag else (
                    f"Platform confirmed exact flag: {confirmed_flag}; solver returned a different flag"
                )
                self._evidence = ()
                self._solution_steps = ()
                self._exp_paths = ()
                self._exp_run_command = ""
                if same_flag and output.evidence:
                    self._evidence = tuple(str(item)[:1000] for item in output.evidence[:20])
                    self._findings += " | Evidence: " + " ; ".join(self._evidence[:5])
                if same_flag:
                    self._solution_steps = tuple(str(item)[:2000] for item in output.solution_steps[:30])
                    self._exp_paths = tuple(str(item) for item in output.exp_paths[:12])
                    self._exp_run_command = output.exp_run_command[:1000]
                # A model response is only a candidate.  Platform confirmation
                # below is the only path that can produce a final success.
                if self.deps.confirmed_flag:
                    self._confirmed = True
            elif isinstance(output, (SolverBlocked, SolverNeedsInput)):
                self._findings = output.message or output.reason
                self.tracer.event(
                    "blocked",
                    reason=output.reason,
                    required=output.required,
                )
                if not self.deps.confirmed_flag:
                    return self._result(BLOCKED if isinstance(output, SolverBlocked) else NEEDS_INPUT)
            elif isinstance(output, SolverGaveUp):
                self._findings = output.findings_summary[:2000]
            # Platform confirmation always counts (the primary path when not in dry-run).
            if self.deps.confirmed_flag:
                self._confirmed = True
                self._flag = self.deps.confirmed_flag

            if self._confirmed and self._flag:
                return self._result(FLAG_FOUND)
            if self._flag:
                return self._result(CANDIDATE_FOUND)
            return self._result(GAVE_UP)

        except asyncio.CancelledError:
            return self._result(CANCELLED)
        except TimeoutError:
            self._findings = "Solver attempt timed out"
            return self._result(TIMED_OUT)
        except ToolBudgetExceededError as e:
            self._findings = str(e)
            return self._result(BUDGET_EXHAUSTED)
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error: {e}", exc_info=True)
            self._findings = f"Error: {e}"
            self.tracer.event("error", error=str(e))
            return self._result(ERROR)

    def bump(self, insights: str) -> None:
        """Inject insights from siblings and prepare to resume."""
        bump_msg = ModelRequest(
            parts=[
                UserPromptPart(
                    content=(
                        "Your previous attempt did not find the flag. Here are insights "
                        "from other agents working on the same challenge:\n\n"
                        f"{insights}\n\n"
                        "Use these insights to try a different approach. "
                        "Do NOT repeat what has already been tried."
                    )
                )
            ]
        )
        self._messages.append(bump_msg)
        self.loop_detector.reset()
        self.tracer.event("bump", insights_chars=len(insights))
        logger.info(f"[{self.agent_name}] Bumped with sibling insights")

    def _result(self, status: str, run_steps: int | None = None, run_cost: float | None = None) -> SolverResult:
        if self.deps.confirmed_flag:
            if self._flag and self._flag.strip() != self.deps.confirmed_flag.strip():
                self._evidence = ()
                self._solution_steps = ()
                self._exp_paths = ()
                self._exp_run_command = ""
            self._confirmed = True
            self._flag = self.deps.confirmed_flag
            status = FLAG_FOUND
        agent_usage = self.cost_tracker.by_agent.get(self.agent_name)
        cost = agent_usage.cost_usd if agent_usage else 0.0
        self.tracer.event(
            "finish", status=status, flag=self._flag, confirmed=self._confirmed,
            cost_usd=round(cost, 4),
            run_id=str(getattr(self.settings, "challenge_run_id", "") or ""),
        )
        return SolverResult(
            flag=self._flag,
            status=status,
            findings_summary=self._findings[:2000],
            step_count=run_steps if run_steps is not None else self._step_count[0],
            cost_usd=run_cost if run_cost is not None else cost,
            log_path=self.tracer.path,
            evidence=self._evidence,
            role=self.role,
            total_cost_usd=cost,
            solution_steps=self._solution_steps,
            exp_paths=self._exp_paths,
            exp_run_command=self._exp_run_command,
            model_spec=self.model_spec,
        )

    async def stop(self) -> None:
        self.tracer.event("stop", step_count=self._step_count[0])
        self.tracer.close()
        if self._owns_sandbox and self.sandbox:
            await self.sandbox.stop()

    def detach_sandbox(self) -> DockerSandbox | None:
        sandbox = self.sandbox
        self.sandbox = None
        self._owns_sandbox = False
        return sandbox
