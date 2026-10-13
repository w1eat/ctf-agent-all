"""Challenge category filtering shared by all coordinator paths."""

from __future__ import annotations

import re

_ALIASES: dict[str, set[str]] = {
    "pwn": {"pwn", "binary exploitation"},
    "web": {"web", "web security", "websec"},
    "crypto": {"crypto", "cryptography"},
    "reverse": {"reverse", "reversing", "rev"},
    "forensics": {"forensics", "forensic", "取证"},
    "stego": {"stego", "steganography", "隐写"},
    "misc": {"misc", "miscellaneous"},
    "mobile": {"mobile", "android", "ios", "app"},
    "osint": {"osint", "open source intelligence"},
    "blockchain": {"blockchain", "web3", "smart contract"},
}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace("_", " ").replace("-", " "))


def normalize_challenge_types(values: list[str] | tuple[str, ...] | set[str]) -> set[str]:
    """Normalize CLI/config values to canonical category names."""
    aliases = {alias: canonical for canonical, names in _ALIASES.items() for alias in names}
    result: set[str] = set()
    for raw in values:
        for item in raw.split(","):
            cleaned = _clean(item)
            if cleaned:
                result.add(aliases.get(cleaned, cleaned))
    return result
