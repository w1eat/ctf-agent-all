"""Click CLI entry point."""

from __future__ import annotations

import asyncio
import logging
import sys
import time
import uuid
from contextlib import nullcontext
from pathlib import Path

import click
from rich.console import Console

from backend.challenge_filter import normalize_challenge_types
from backend.config import Settings
from backend.models import DEFAULT_MODELS
from backend.tracing import _safe_run_id, observe_exit_signals, prune_run_logs, run_text_log

console = Console()


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiodocker").setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%X"))
    logging.basicConfig(level=level, handlers=[handler], force=True)


@click.command()
@click.option("--platform", default=None, type=click.Choice(["auto", "ctfd", "local"]), help="Platform backend (default: auto)")
@click.option("--platform-url", default=None, help="Platform URL (used by auto mode)")
@click.option("--browser-profile", default=None, help="Persistent Playwright browser profile directory")
@click.option("--ctfd-url", default=None, help="CTFd URL (overrides .env)")
@click.option("--ctfd-token", default=None, help="CTFd API token (overrides .env)")
@click.option("--image", default="ctf-sandbox", help="Docker sandbox image name")
@click.option("--models", multiple=True, help="Model specs (default: all configured)")
@click.option("--challenge", default=None, help="Solve a single challenge directory")
@click.option("--challenges-dir", default="challenges", help="Directory for challenge files")
@click.option(
    "--solver-mcp-config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="JSON config enabling IDA, JADX, and Kali MCP tools for every Solver.",
)
@click.option(
    "--challenge-type",
    "challenge_types",
    multiple=True,
    help="Prefer selected challenge categories, e.g. pwn; repeat or comma-separate values.",
)
@click.option("--no-submit", is_flag=True, help="Dry run — don't submit flags")
@click.option("--submit", is_flag=True, help="Allow flag submission (disabled by default)")
@click.option("--login", is_flag=True, help="Open headed browser and wait for one manual platform login")
@click.option("--coordinator-model", default=None, help="Model for coordinator (default: claude-opus-4-6)")
@click.option("--writeup-model", default=None, help="Override the model used for Chinese writeups")
@click.option("--coordinator", default="claude", type=click.Choice(["claude", "codex"]), help="Coordinator backend")
@click.option(
    "--coordinator-full-access/--no-coordinator-full-access",
    default=False,
    help="Give the Coordinator unrestricted native agent tools and host execution access.",
)
@click.option(
    "--max-challenges",
    default=10,
    type=click.IntRange(min=1),
    help="Max challenges solved concurrently",
)
@click.option(
    "--max-preparations",
    default=None,
    type=click.IntRange(min=1),
    help="Max challenge packages prepared concurrently (default: 4)",
)
@click.option("--msg-port", default=0, type=int, help="Operator message port (0 = auto)")
@click.option("--resume-run", default=None, help="Resume a persisted challenge state run")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging")
def main(
    platform: str | None,
    platform_url: str | None,
    browser_profile: str | None,
    ctfd_url: str | None,
    ctfd_token: str | None,
    image: str,
    models: tuple[str, ...],
    challenge: str | None,
    challenges_dir: str,
    solver_mcp_config: Path | None,
    challenge_types: tuple[str, ...],
    no_submit: bool,
    submit: bool,
    login: bool,
    coordinator_model: str | None,
    writeup_model: str | None,
    coordinator: str,
    coordinator_full_access: bool,
    max_challenges: int,
    max_preparations: int | None,
    msg_port: int,
    resume_run: str | None,
    verbose: bool,
) -> None:
    """CTF Agent — multi-model solver swarm.

    Run without --challenge to start the full coordinator (Ctrl+C to stop).
    """
    _setup_logging(verbose)

    settings = Settings(sandbox_image=image)
    settings.challenge_run_id = resume_run or uuid.uuid4().hex
    if not resume_run:
        from backend.local_knowledge import pin_local_snapshot

        try:
            local_snapshot = pin_local_snapshot(settings.challenge_run_id)
            logging.info("Run %s uses local knowledge snapshot %s",
                         settings.challenge_run_id, local_snapshot or "none")
        except (OSError, ValueError) as exc:
            logging.warning("Could not pin local knowledge snapshot: %s", exc)
    if settings.external_knowledge_enabled:
        from backend.external_knowledge import pin_snapshot
        try:
            legacy_run = bool(resume_run and not (Path(settings.external_knowledge_dir) / "runs" / (settings.challenge_run_id + ".json")).exists())
            pinned = pin_snapshot(settings.external_knowledge_dir, settings.challenge_run_id)
            if legacy_run:
                logging.warning("Resumed run %s had no knowledge manifest; pinned current snapshot %s",
                                settings.challenge_run_id, pinned or "none")
            if pinned:
                logging.info("Run %s uses knowledge snapshot %s", settings.challenge_run_id, pinned)
        except (OSError, ValueError) as exc:
            logging.warning("Could not pin external knowledge snapshot: %s", exc)
    settings.run_log_stamp = time.strftime("%Y%m%d-%H%M%S")
    if solver_mcp_config:
        settings.solver_mcp_config = str(solver_mcp_config.resolve())
    if platform:
        settings.platform = platform
    if platform_url:
        settings.platform_url = platform_url
    elif ctfd_url:
        settings.platform_url = ctfd_url
    if browser_profile:
        settings.browser_profile_dir = browser_profile
    if ctfd_url:
        settings.ctfd_url = ctfd_url
    if ctfd_token:
        settings.ctfd_token = ctfd_token
    settings.max_concurrent_challenges = max_challenges
    if max_preparations is not None:
        settings.preparation_concurrency = max_preparations
    settings.challenge_types = sorted(normalize_challenge_types(challenge_types))
    settings.platform_login = login
    settings.coordinator_full_access = coordinator_full_access
    if writeup_model:
        settings.writeup_model_spec = writeup_model
    no_submit = no_submit or not submit

    if challenge and submit:
        raise click.UsageError(
            "--submit requires the coordinator's Playwright platform flow; "
            "do not combine it with --challenge. Use --platform auto without --challenge."
        )

    if models:
        model_specs = list(models)
    elif settings.model_name:
        model_specs = [f"openai/{settings.model_name}"]
    else:
        model_specs = list(DEFAULT_MODELS)

    log_context = nullcontext() if challenge else run_text_log(
        settings.challenge_run_id, settings.run_log_stamp
    )
    with log_context:
        console.print("[bold]CTF Agent v2[/bold]")
        console.print(f"  Platform: {settings.platform} ({settings.platform_url or settings.ctfd_url})")
        console.print(f"  Models: {', '.join(model_specs)}")
        console.print(
            f"  Writeup model: {settings.writeup_model_spec or f'Solver model (fallback: {model_specs[0]})'}"
        )
        console.print(f"  Image: {settings.sandbox_image}")
        console.print(f"  Run ID: {settings.challenge_run_id}")
        if not challenge:
            safe_log_id = _safe_run_id(settings.challenge_run_id)
            console.print(
                f"  Trace: logs/coordinator-{safe_log_id}-{settings.run_log_stamp}.jsonl"
            )
            console.print(
                f"  Terminal log: logs/run-{safe_log_id}-{settings.run_log_stamp}.log"
            )
        console.print(f"  Max challenges: {max_challenges}")
        console.print(f"  Max preparations: {settings.preparation_concurrency}")
        console.print(f"  Coordinator full access: {'ENABLED' if settings.coordinator_full_access else 'disabled'}")
        if settings.challenge_types:
            console.print(f"  Challenge types: {', '.join(settings.challenge_types)}")
        console.print()

        if challenge:
            asyncio.run(_run_single(settings, challenge, model_specs, no_submit, max_challenges))
        else:
            from backend.platforms.browser_mcp import BrowserProfileInUseError

            try:
                asyncio.run(_run_coordinator(settings, model_specs, challenges_dir, no_submit,
                                             coordinator_model, coordinator, max_challenges, msg_port))
            except BrowserProfileInUseError as exc:
                console.print(f"[red]{exc}[/red]")
                sys.exit(1)
            finally:
                try:
                    prune_run_logs(keep_run=(settings.challenge_run_id, settings.run_log_stamp))
                except OSError as exc:
                    print(f"Run log retention failed: {exc}", file=sys.stderr, flush=True)


async def _run_single(
    settings: Settings,
    challenge_dir: str,
    model_specs: list[str],
    no_submit: bool,
    max_challenges: int,
) -> None:
    """Run a single challenge with a swarm."""
    from backend.agents.swarm import ChallengeSwarm
    from backend.cost_tracker import CostTracker
    from backend.platforms.local import LocalPlatformAdapter
    from backend.prompts import ChallengeMeta
    from backend.sandbox import cleanup_orphan_containers, configure_semaphore
    from backend.solver_mcp import SolverMcpGateway

    max_containers = max_challenges * len(model_specs)
    configure_semaphore(max_containers)
    await cleanup_orphan_containers()

    challenge_path = Path(challenge_dir)
    meta_path = challenge_path / "metadata.yml"
    if not meta_path.exists():
        console.print(f"[red]No metadata.yml found in {challenge_dir}[/red]")
        sys.exit(1)

    meta = ChallengeMeta.from_yaml(meta_path)
    console.print(f"[bold]Challenge:[/bold] {meta.name} ({meta.category}, {meta.value} pts)")

    platform = LocalPlatformAdapter(str(challenge_path.parent), settings=settings, allow_submit=False)
    await platform.start()
    cost_tracker = CostTracker()
    analysis_gateway = None
    try:
        package_state = await platform.get_challenge_state(meta.name)
        if package_state.get("state") == "waiting_for_environment" and meta.environment.get("source") in ("compose", "docker-compose"):
            await platform.start_environment(meta.name)
            package_state = await platform.get_challenge_state(meta.name)
        if package_state.get("state") != "ready":
            raise click.ClickException(
                f"Challenge {meta.name!r} is not ready: {package_state.get('reason') or package_state.get('state')}"
            )
        meta.connection_info = package_state.get("connection_info") or meta.connection_info
        meta.environment = package_state.get("environment") or meta.environment

        analysis_gateway = SolverMcpGateway(settings.solver_mcp_config) if settings.solver_mcp_config else None
        if analysis_gateway:
            await analysis_gateway.start()
            await analysis_gateway.register_challenge(meta.name, challenge_path)

        from backend.solver_base import CANDIDATE_FOUND, FLAG_FOUND, VERIFIED
        from backend.writeups import WriteupManager

        manager = WriteupManager(settings, default_model_spec=settings.writeup_model_spec or model_specs[0])
        swarm = ChallengeSwarm(
            challenge_dir=str(challenge_path),
            meta=meta,
            platform=platform,
            cost_tracker=cost_tracker,
            settings=settings,
            model_specs=model_specs,
            no_submit=no_submit,
            analysis_gateway=analysis_gateway,
            writeup_manager=manager,
        )
        result = await swarm.run()
        if result and result.flag and result.status in (CANDIDATE_FOUND, FLAG_FOUND, VERIFIED):
            source = "candidate_found"
            if result.status == VERIFIED and len(result.verified_by) >= settings.flag_verification_quorum:
                source = "independent_quorum"
            elif result.status == FLAG_FOUND and not no_submit:
                try:
                    if meta.name in await platform.get_solve_status():
                        source = "platform_confirmed"
                except Exception:
                    logging.exception("Could not check platform confirmation for %s", meta.name)
            label = "FLAG FOUND" if source != "candidate_found" else "FLAG CANDIDATE (unverified)"
            console.print(f"\n[bold green]{label}:[/bold green] {result.flag}")
            try:
                await manager.record_and_schedule(
                    challenge_path, meta, result.flag, source,
                    solver_result=result,
                    model_spec=settings.writeup_model_spec or result.model_spec or model_specs[0],
                )
            except Exception:
                logging.exception("Could not queue writeup for %s", meta.name)
        elif swarm.candidate_registry.records:
            console.print("\n[yellow]Flag candidate recorded; writeup queued without confirmation.[/yellow]")
        else:
            console.print("\n[bold red]No flag found.[/bold red]")

        await manager.wait_for_pending(
            timeout=settings.writeup_timeout_seconds + settings.writeup_replay_timeout_seconds + 90
        )
        writeup_path = challenge_path / "writeup.md"
        if writeup_path.exists():
            console.print(f"[bold]Writeup:[/bold] {writeup_path}")
        elif swarm.candidate_registry.records or (result and result.flag):
            console.print(f"[yellow]Writeup pending or failed; see {challenge_path / 'solution' / 'manifest.json'}[/yellow]")

        console.print("\n[bold]Cost Summary:[/bold]")
        for agent_name in cost_tracker.by_agent:
            console.print(f"  {agent_name}: {cost_tracker.format_usage(agent_name)}")
        console.print(f"  [bold]Total: ${cost_tracker.total_cost_usd:.2f}[/bold]")
    finally:
        if analysis_gateway:
            await analysis_gateway.release_challenge(meta.name)
            await analysis_gateway.close()
        await platform.close()


async def _run_coordinator(
    settings: Settings,
    model_specs: list[str],
    challenges_dir: str,
    no_submit: bool,
    coordinator_model: str | None,
    coordinator_backend: str,
    max_challenges: int,
    msg_port: int = 0,
) -> None:
    """Run the full coordinator (continuous until Ctrl+C)."""
    from backend.sandbox import cleanup_orphan_containers, configure_semaphore

    max_containers = max_challenges * len(model_specs)
    configure_semaphore(max_containers)
    await cleanup_orphan_containers()
    console.print(f"[bold]Starting coordinator ({coordinator_backend}, Ctrl+C to stop)...[/bold]\n")

    with observe_exit_signals():
        if coordinator_backend == "codex":
            from backend.agents.codex_coordinator import run_codex_coordinator
            results = await run_codex_coordinator(
                settings=settings,
                model_specs=model_specs,
                challenges_root=challenges_dir,
                no_submit=no_submit,
                coordinator_model=coordinator_model,
                msg_port=msg_port,
            )
        else:
            from backend.agents.claude_coordinator import run_claude_coordinator
            results = await run_claude_coordinator(
                settings=settings,
                model_specs=model_specs,
                challenges_root=challenges_dir,
                no_submit=no_submit,
                coordinator_model=coordinator_model,
                msg_port=msg_port,
            )

    if results.get("error"):
        raise click.ClickException(str(results["error"]))
    console.print("\n[bold]Final Results:[/bold]")
    for challenge, data in results.get("results", {}).items():
        console.print(f"  {challenge}: {data.get('flag', 'no flag')}")
    console.print(f"\n[bold]Total cost: ${results.get('total_cost_usd', 0):.2f}[/bold]")


@click.command()
@click.argument("message")
@click.option("--port", default=9400, type=int, help="Coordinator message port")
@click.option("--host", default="127.0.0.1", help="Coordinator host")
def msg(message: str, port: int, host: str) -> None:
    """Send a message to the running coordinator."""
    import json
    import urllib.request

    body = json.dumps({"message": message}).encode()
    req = urllib.request.Request(
        f"http://{host}:{port}/msg",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            console.print(f"[green]Sent:[/green] {data.get('queued', message[:200])}")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        console.print("Is the coordinator running?")
        sys.exit(1)


if __name__ == "__main__":
    main()
