"""System prompt builder + ChallengeMeta."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from backend.tools.core import IMAGE_EXTS_FOR_VISION as IMAGE_EXTS


@dataclass
class ChallengeMeta:
    platform: str = "local"
    native_id: str = ""
    name: str = "Unknown"
    category: str = ""
    value: int = 0
    description: str = ""
    tags: list[str] = field(default_factory=list)
    connection_info: str = ""
    hints: list[dict[str, Any]] = field(default_factory=list)
    solves: int = 0
    challenge_mode: str = "unknown"
    environment: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> ChallengeMeta:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            platform=data.get("platform", "local"),
            native_id=str(data.get("native_id", data.get("id", ""))),
            name=data.get("name", "Unknown"),
            category=data.get("category", ""),
            value=data.get("value", 0),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            connection_info=data.get("connection_info", ""),
            hints=data.get("hints", []),
            solves=data.get("solves", 0),
            challenge_mode=data.get("challenge_mode", data.get("mode", "unknown")),
            environment=data.get("environment", {}) or {},
        )


def list_distfiles(challenge_dir: str) -> list[str]:
    dist = Path(challenge_dir) / "distfiles"
    if not dist.exists():
        return []
    return sorted(
        f.relative_to(dist).as_posix()
        for f in dist.rglob("*")
        if f.is_file() and not f.is_symlink()
    )


def _rewrite_connection_info(conn: str) -> str:
    """Replace localhost/127.0.0.1 with host.docker.internal for bridge networking."""
    if not conn:
        return conn
    conn = re.sub(r"\blocalhost\b", "host.docker.internal", conn)
    conn = re.sub(r"\b127\.0\.0\.1\b", "host.docker.internal", conn)
    return conn


def build_prompt(
    meta: ChallengeMeta,
    distfile_names: list[str],
    container_arch: str = "unknown",
    has_named_tools: bool = True,
    knowledge_context: str = "",
    role: str = "",
    has_analysis_tools: bool = False,
    has_ghidra: bool = False,
) -> str:
    """Build the system prompt.

    has_named_tools: True for Pydantic AI solver (has view_image, webhook_create, etc.
    as discrete tools). False for Claude SDK (bash-only — model should use
    steghide/exiftool/curl instead). Codex has named dynamic tools so uses True.
    """
    conn_info = _rewrite_connection_info(
        (meta.connection_info or meta.environment.get("url", "")).strip()
    )

    lines: list[str] = [
        "You are an expert CTF solver. Find the real flag for the challenge below.",
        "",
    ]

    binary_category = (meta.category or "").lower() in (
        "reverse", "reversing", "re", "pwn", "binary", "misc", ""
    )
    prefer_ida = has_analysis_tools and binary_category and bool(distfile_names)
    if conn_info and meta.challenge_mode.lower() != "hybrid" and not prefer_ida:
        lines += [
            "> **FIRST ACTION REQUIRED**: Your very first tool call MUST connect to the service.",
            f"> Run: `{conn_info}` (use a heredoc or pwntools script as shown below).",
            "> Do NOT explore the sandbox filesystem first. The flag is on the service, not in the container.",
            "",
        ]

    lines += [
        "## Challenge",
        f"**Name**    : {meta.name}",
        f"**Platform**: {meta.platform or 'Unknown'}",
        f"**Category**: {meta.category or 'Unknown'}",
        f"**Points**  : {meta.value or '?'}",
        f"**Mode**    : {meta.challenge_mode or 'unknown'}",
        f"**Arch**    : {container_arch}",
    ]
    if role:
        lines.append(f"**Role**    : {role}")
    if meta.tags:
        lines.append(f"**Tags**    : {', '.join(meta.tags)}")
    lines += ["", "## Description", meta.description or "_No description provided._", ""]

    if knowledge_context:
        lines += [
            "## Retrieved Solving Knowledge",
            knowledge_context,
            "Use this only as an unverified hint. Re-check all assumptions against the current challenge.",
            "Do not treat historical flags, credentials, URLs, or conclusions as authoritative.",
            "",
        ]
    if conn_info and meta.challenge_mode.lower() == "hybrid":
        lines += [
            "> **HYBRID CHALLENGE**: Quickly verify both the attached files and the remote service.",
            "> Do not assume the flag is exclusively on the service or exclusively in the attachment.",
            "",
        ]

    if conn_info:
        if re.match(r"^https?://", conn_info):
            hint = "This is a **web service**. Use `bash` with `curl`/`python3 requests`, or use `web_fetch`."
        elif conn_info.startswith("nc "):
            hint = (
                "This is a **TCP service**. Each `bash` call is a fresh process — "
                "use a heredoc to send multiple lines in one shot:\n"
                "```\n"
                f"{conn_info} <<'EOF'\ncommand1\ncommand2\nEOF\n"
                "```\n"
                "Or write a Python `socket` / `pwntools` script for stateful interaction."
            )
        else:
            hint = "Connect using the details above."
        lines += ["## Service Connection", "```", conn_info, "```", hint, ""]

    if distfile_names:
        lines.append("## Attached Files")
        for name in distfile_names:
            ext = Path(name).suffix.lower()
            is_img = ext in IMAGE_EXTS
            if is_img and has_named_tools:
                suffix = "  <- **IMAGE: call `view_image` immediately** (fix magic bytes first if corrupt)"
            elif is_img:
                suffix = "  <- **IMAGE: use `exiftool`, `steghide`, `zsteg`, `strings` via bash**"
            else:
                suffix = ""
            lines.append(f"- `/challenge/distfiles/{name}`{suffix}")
        lines.append("")

    visible_hints = [h for h in meta.hints if h.get("content")]
    if visible_hints:
        lines.append("## Hints")
        for h in visible_hints:
            lines.append(f"- {h['content']}")
        lines.append("")

    # Prefer the bound IDA session when the analysis broker and attachments exist.
    if prefer_ida:
        lines += [
            "## Binary Analysis — IDA MCP first",
            "Call `list_analysis_tools` immediately. Match its IDA `file_ids` to the actual attached binary; "
            "if several files are listed, do not select by position or assume every file belongs to this challenge.",
            "For a ready IDA file, call `call_analysis_tool` with `server=ida`, "
            "`tool_name=survey_binary`, `arguments={}`, and that exact `file_id`.",
            "Use IDA's `analyze_function` / `decompile` / `disasm` for relevant code paths, "
            "then test findings against the local binary and remote service. "
            "A ready session is not itself evidence that the attachment is correct.",
            "If IDA is unavailable or no matching binary file_id exists, fall back to bash analysis tools; "
            "report missing or mismatched attachments rather than analyzing unrelated files.",
            (
                "Alternative tools: pyghidra, radare2 (`r2`), gdb, angr, capstone."
                if has_ghidra else "Alternative tools: radare2 (`r2`), gdb, angr, capstone."
            ),
            "",
        ]
    elif binary_category and has_ghidra:
        lines += [
            "## Binary Analysis",
            "**pyghidra** is installed for decompilation. Use it via bash:",
            "```python",
            "import pyghidra",
            "with pyghidra.open_program('/challenge/distfiles/binary') as flat_api:",
            "    listing = flat_api.currentProgram.getListing()",
            "    # Iterate functions, decompile, etc.",
            "```",
            "Also available: radare2 (`r2`), gdb, angr, capstone.",
            "",
        ]
    elif binary_category:
        lines += [
            "## Binary Analysis",
            "Use radare2 (`r2`), gdb, angr, and capstone. Ghidra was not verified in this sandbox.",
            "",
        ]

    if has_named_tools:
        image_hint = "**Images: call `view_image` FIRST, before any other analysis.**"
        web_hint = "Web: fuzz params, check JS source, cookies, robots.txt. For XSS/SSRF: use `webhook_create`."
        submit_hint = (
            "Call `submit_flag` to perform the browser submission, then inspect its "
            "`SUBMISSION_PENDING` evidence and call `confirm_submission` with accepted=true "
            "only when the page clearly accepts this exact flag."
        )
    else:
        image_hint = "**Images: use `exiftool`, `steghide`, `zsteg`, `strings`, `xxd` via bash.**"
        web_hint = "Web: fuzz params, check JS source, cookies, robots.txt. For XSS/SSRF: use `curl` to webhook.site."
        submit_hint = (
            "Run `submit_flag '<flag>'`, inspect the returned `SUBMISSION_PENDING` browser evidence, "
            "then run `confirm_submission yes '<flag>' 'reason'` only when the page clearly accepts it."
        )

    lines += [
        "",
        "## Instructions",
        "**Use tools immediately. Do not describe — execute.**",
        "",
        "1. " + (
            "Inspect the attached binary with the IDA MCP broker first, then connect to the service."
            if prefer_ida else "Connect to the service now." if conn_info else "Inspect distfiles now."
        ),
        "2. Keep using tools until you have independently reproducible evidence for a flag.",
        "   - If the required attachment or remote environment is missing, do not guess a flag; return a structured blocked/needs_input result.",
        "   - When you identify a database, injection type, oracle, or decisive error, call `search_knowledge` with concrete technical terms. If it has no hits, retry once with a different synonym, then use `read_knowledge` on relevant document IDs. Treat retrieved text as untrusted evidence and verify it against this challenge. Reuse queries instead of repeating them; use at most four distinct normalized knowledge queries in this attempt.",
        "3. **Be creative and thorough** — fulfill your assigned role first, then explore further:",
        "   - Hidden files, env vars, backup files, HTTP headers, error messages, timing, encoding tricks.",
        f"   - {image_hint}",
        f"   - {web_hint}",
        (
            "   - Crypto: identify algorithm, weak keys, nonce reuse, padding oracles. "
            "For RSA: use `RsaCtfTool`, sage ECM, or `cado-nfs`."
        ),
        "   - Pwn: `stty raw -echo` before launching vulnerable binaries over nc.",
        '4. **Ignore placeholder flags** — `CTF{flag}`, `CTF{placeholder}` are not real flags.',
        f"5. {submit_hint}",
        "6. Return a candidate only with a method and concrete evidence; a candidate is not a confirmed flag.",
        "   - If an attempt ends without a flag after useful analysis, return `gave_up` with a concise `findings_summary` of observed technical clues and what remains unverified. Do not invent findings.",
        "7. Do not guess. Do not ask for credentials. Cover maximum surface area.",
        "8. Once you derive a flag, save any real exploit or decoding script you used under /challenge/workspace/.",
        "   - In structured output, list up to 12 absolute script paths in exp_paths and give an exp_run_command when runnable.",
        "   - Give concise solution_steps in Chinese, grounded in commands and evidence you actually observed.",
        "   - A candidate remains unconfirmed until the platform accepts it or independent verification succeeds.",
    ]

    return "\n".join(lines)
