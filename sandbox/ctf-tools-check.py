#!/usr/bin/env python3
"""Check the sandbox's documented tools and generate its reference file."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_MANIFEST = Path(os.environ.get("CTF_TOOL_MANIFEST", "/opt/ctf/tool-manifest.json"))


def check_tools(manifest: dict) -> dict:
    categories: dict[str, list[dict]] = {}
    for category, tools in manifest["categories"].items():
        results = []
        for tool in tools:
            command = tool.get("command")
            module = tool.get("module")
            if bool(command) == bool(module):
                raise ValueError(f"{category}/{tool['name']}: specify one command or module")
            if command:
                found = shutil.which(command)
                result = {"name": tool["name"], "kind": "command", "target": command,
                          "available": found is not None, "path": found}
            else:
                interpreter = tool.get("interpreter", sys.executable)
                try:
                    completed = subprocess.run(
                        [interpreter, "-c", f"import {module}"], capture_output=True,
                        text=True, timeout=90, check=False,
                    )
                    result = {"name": tool["name"], "kind": "module", "target": module,
                              "available": completed.returncode == 0}
                    if completed.returncode:
                        result["error"] = completed.stderr.strip()[-1000:]
                except (OSError, subprocess.TimeoutExpired) as exc:
                    result = {"name": tool["name"], "kind": "module", "target": module,
                              "available": False, "error": str(exc)}
            results.append(result)
        categories[category] = results
    architecture = platform.machine()
    ok = architecture == manifest["target_architecture"] and all(
        tool["available"] for tools in categories.values() for tool in tools
    )
    return {"ok": ok, "architecture": architecture,
            "target_architecture": manifest["target_architecture"], "categories": categories}


def render_reference(manifest: dict) -> str:
    lines = ["CTF SANDBOX TOOLS", "=================", "",
             "Validated by: ctf-tools-check --json",
             f"Architecture: linux/amd64 ({manifest['target_architecture']})",
             "Distfiles: /challenge/distfiles/ (read-only)",
             "Workspace: /challenge/workspace/ (writable)", ""]
    for category, tools in manifest["categories"].items():
        lines.extend([f"== {category.upper()} =="])
        for tool in tools:
            target = tool.get("command") or f"python3 import {tool['module']}"
            lines.append(f"{tool['name']}: {target} — {tool['use']}")
        lines.append("")
    lines.extend([
        "Use python3 -m playwright install chromium only when rebuilding the image;",
        "the browser is preinstalled in the built image.",
        "Android dynamic analysis requires a reachable external device or emulator.",
        "Challenge Compose environments are started by the host manager, not inside this image.",
        "PyGhidra uses GHIDRA_INSTALL_DIR=/opt/ghidra.",
        "ML challenge Keras uses the torch backend.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable status")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--write-reference", type=Path, help="write /tools.txt only if all checks pass")
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = check_tools(manifest)
    if args.write_reference and result["ok"]:
        args.write_reference.write_text(render_reference(manifest), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        for category, tools in result["categories"].items():
            failures = [tool["name"] for tool in tools if not tool["available"]]
            print(f"{category}: {'OK' if not failures else 'MISSING ' + ', '.join(failures)}")
        if result["architecture"] != result["target_architecture"]:
            print(f"architecture: expected {result['target_architecture']}, got {result['architecture']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
