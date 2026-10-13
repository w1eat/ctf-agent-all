"""Preflight, build and verify the linux/amd64 CTF sandbox image."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIB = 1024**3


def run(args: list[str], *, capture: bool = False, timeout: int | None = None) -> str:
    result = subprocess.run(
        args, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        capture_output=capture, timeout=timeout, check=False,
    )
    if result.returncode:
        detail = ((result.stdout or "") + (result.stderr or "")).strip()[-4000:] if capture else "see command output"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return result.stdout.strip() if capture else ""


def preflight(min_free_gib: int) -> tuple[int, str]:
    try:
        run(["docker", "info", "--format", "{{.ServerVersion}}"], capture=True, timeout=20)
        root_dir = run(["docker", "info", "--format", "{{.DockerRootDir}}"],
                       capture=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
        raise RuntimeError("Docker Engine is unavailable. Start Docker Desktop first.") from exc
    output = run(
        ["docker", "run", "--rm", "ubuntu:22.04", "df", "-B1", "--output=avail", "/"],
        capture=True, timeout=120,
    )
    free_bytes = int(output.splitlines()[-1].strip())
    if free_bytes < min_free_gib * GIB:
        raise RuntimeError(
            f"Docker filesystem has {free_bytes / GIB:.1f} GiB free; "
            f"at least {min_free_gib} GiB is required for this full image build."
        )
    print(f"Docker data root: {root_dir}; filesystem free: {free_bytes / GIB:.1f} GiB", flush=True)
    return free_bytes, root_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="ctf-sandbox")
    parser.add_argument("--min-free-gib", type=int, default=30)
    parser.add_argument("--skip-build", action="store_true", help="verify an existing image")
    args = parser.parse_args()
    if args.min_free_gib < 1:
        parser.error("--min-free-gib must be positive")
    free_bytes, root_dir = preflight(args.min_free_gib)
    started = time.monotonic()
    if not args.skip_build:
        run(["docker", "build", "--platform", "linux/amd64", "--progress=plain",
             "-f", "sandbox/Dockerfile.sandbox", "-t", args.image, "."])
    build_seconds = time.monotonic() - started
    status = json.loads(run(["docker", "run", "--rm", args.image,
                             "ctf-tools-check", "--json"], capture=True, timeout=300))
    if not status["ok"]:
        raise RuntimeError("ctf-tools-check reported missing tools")
    reference = run(["docker", "run", "--rm", args.image, "cat", "/tools.txt"],
                    capture=True, timeout=60)
    manifest = json.loads((ROOT / "sandbox" / "tool-manifest.json").read_text(encoding="utf-8"))
    expected_names = [tool["name"] for tools in manifest["categories"].values() for tool in tools]
    missing_reference = [name for name in expected_names if f"{name}: " not in reference]
    if missing_reference:
        raise RuntimeError(f"/tools.txt is missing manifest entries: {missing_reference}")
    if "podman" in reference.lower():
        raise RuntimeError("/tools.txt still advertises nested Podman")
    smoke = json.loads(run([
        "docker", "run", "--rm", "--cap-add", "SYS_PTRACE", "--security-opt",
        "seccomp=unconfined", args.image, "python3", "/opt/ctf/smoke.py", "--json",
    ], capture=True, timeout=900))
    if not smoke["ok"]:
        raise RuntimeError("Sandbox category smoke test failed")
    if set(smoke["categories"]) != set(manifest["categories"]):
        raise RuntimeError("Smoke categories do not match the tool manifest")
    size = int(run(["docker", "image", "inspect", "--format", "{{.Size}}", args.image],
                   capture=True, timeout=20))
    report = {"image": args.image, "architecture": status["architecture"],
              "image_bytes": size, "build_seconds": round(build_seconds, 1),
              "docker_data_root": root_dir, "docker_free_bytes_before": free_bytes,
              "tool_check": status, "reference_entries_checked": len(expected_names),
              "smoke": smoke}
    output = ROOT / "logs" / "sandbox-build-report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Validated {args.image}: {size / GIB:.2f} GiB; report: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Sandbox build/verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
